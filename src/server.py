
import sys
sys.path.append('..')
import argparse
import socket
import threading
import time
from lib.log import Logger
from lib.mutex import Mutex
from lib.connection import Connection
from lib.constant import *
from lib.redis_client import Redis
from lib.parse import *
from lib.database import Database
from lib.messages import Messages
from lib.handle import handle_recieve_event
from lib.command import usecase_command
from lib.user import User
from internal_client import InternalClient

log = Logger('SERVER').get_logger()

# Initialize parser
parser = argparse.ArgumentParser()

class Server:
    def __init__(self,host="127.0.0.1",port=5000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.do_running = True
        self.BUFFER_SIZE = 2048
        self.topic = "SERVER_TO_SERVER"
        self.internal_clients = dict()
        self.connection_clients = dict()
        self.server_mutex = Mutex()
        self.redis_publisher = Redis()
        self.redis_subscriber = Redis()
        self.database = Database()
        self.messages = Messages()
        self.users = User()
        self.redis_subscriber.subscribe(self.topic)

        self.redis_publisher_mutex_id = "redis_publisher"
        self.redis_subscriber_mutex_id = "redis_subscriber"
        self.internal_client_mutex_id = "internal_clients"
        self.connection_client_mutex_id = "connection_clients"
        self.message_mutex_id = "messages"
        self.user_mutex_id = "users"
        self.database_mutex_id = "database"

        self.initial_lock()
        self.listen()

    def listen(self):
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen()
        except socket.error as e:
            log.error("Socket server error : {}".format(e))
    
    def get_server_name(self):
        return "{}:{}".format(self.host,self.port)
    
    def initial_lock(self):
        self.server_mutex.add_lock(self.internal_client_mutex_id)
        self.server_mutex.add_lock(self.connection_client_mutex_id)
        self.server_mutex.add_lock(self.redis_publisher_mutex_id)
        self.server_mutex.add_lock(self.redis_subscriber_mutex_id)
        self.server_mutex.add_lock(self.message_mutex_id)
        self.server_mutex.add_lock(self.user_mutex_id)
        self.server_mutex.add_lock(self.database_mutex_id)
    
    def get_lock(self,mutex_id):
        return self.server_mutex.get_lock(mutex_id)
    
    def handle_accept(self):
        while self.do_running:
            client, address = self.sock.accept()
            try:
                if client:
                    self.add_connection_client(client,address)
                    log.info('Accepted : ' + address[0] + ':' + str(address[1]))
                    thread = threading.Thread(target=self.handle_receive,args=(client,))
                    thread.setDaemon(True)
                    thread.start()

                self.sleep(0.2)
            except ConnectionResetError:
                self.sub_connection_client(client)
                client.close()
            except OSError:
                self.sub_connection_client(client)
                client.close()
    
    def handle_notify_client(self):
        lock = self.get_lock(self.connection_client_mutex_id)
        lock_database = self.get_lock(self.database_mutex_id)
        while self.do_running:
            with lock:
                for connection_client in self.connection_clients:
                    connection = self.connection_clients[connection_client]

                    if connection.get_type() == "INTERNAL":
                        continue
                    
                    message = ""
                    with lock_database:
                        message = self.database.subscribe(connection.get_username())

                    if not message:
                        continue

                    connection.notify(message)

                    self.sleep(0.0001)

            self.sleep(1)
    
    def apply_payload(self,event,payload,client):
        lock = self.get_lock(self.connection_client_mutex_id)
        lock_message = self.get_lock(self.message_mutex_id)
        lock_database = self.get_lock(self.database_mutex_id)
        lock_user = self.get_lock(self.user_mutex_id)
        lock_internal = self.get_lock(self.internal_client_mutex_id)
        with lock:
            if client.fileno() in self.connection_clients:
                connection = self.connection_clients[client.fileno()]
                usecase_command(
                    event,payload,
                    self.messages,lock_message,
                    self.database,lock_database,
                    self.users,lock_user,
                    connection,
                    self.internal_clients,lock_internal,
                    self.connection_clients
                )

    def handle_receive(self,client):
        try:
            while self.do_running:
                data = client.recv(self.BUFFER_SIZE)
                if data:
                    print("RECIVE DATA : {}".format(data))
                    resp_data = data.decode()
                    if resp_data == "INTERNAL":
                        self.verify_connection_client(client,resp_data)
                        continue

                    event,payload = handle_recieve_event(resp_data)
                    if not event:
                        continue

                    self.apply_payload(event,payload,client)
                else:
                    self.sub_connection_client(client)
                    client.close()

                self.sleep(0.2)
            client.close()
        except ConnectionResetError:
            self.sub_connection_client(client)
            client.close()
        except OSError:
            self.sub_connection_client(client)
            client.close()
    
    def add_connection_client(self,client,address):
        lock = self.get_lock(self.connection_client_mutex_id)
        with lock:
            if client.fileno() not in self.connection_clients:
                connection = Connection(client,address)
                self.connection_clients[connection.get_name()] = connection
                log.info("Added connection : {}".format(connection.get_address()))
    
    def sub_connection_client(self,client):
        lock = self.get_lock(self.connection_client_mutex_id)
        with lock:
            if client.fileno() in self.connection_clients:
                log.info("Disconnected connection : {}".format(
                    self.connection_clients[client.fileno()].get_address()
                ))
                del self.connection_clients[client.fileno()]
    
    def verify_connection_client(self,client,type_name):
        lock = self.get_lock(self.connection_client_mutex_id)
        with lock:
            if client.fileno() in self.connection_clients:
                self.connection_clients[client.fileno()].set_type(type_name)
                log.info("Verify type name client successed")

    def add_internal_client(self,client):
        lock = self.get_lock(self.internal_client_mutex_id)
        with lock:
            if client.get_name() not in self.internal_clients:
                self.internal_clients[client.get_name()] = client
                log.info("Added internal client : {}".format(client.get_name()))
            else:
                log.warning("Internal client : {} already connected..".format(client.get_name()))
    
    def sub_internal_client(self,client_name):
        lock = self.get_lock(self.internal_client_mutex_id)
        with lock:
            if client_name in self.internal_clients:
                del self.internal_clients[client_name]
                log.info("Deleted internal client : {}".format(client_name))
            else:
                log.warning("Internal client : {} has deleted..".format(client_name))

    def new_internal_client(self,host,port):
        try:
            client = InternalClient(host=host,port=port)
            thread = threading.Thread(target=client.run(),args=())
            thread.setDaemon(True)
            thread.start()
            self.add_internal_client(client)
        except Exception as ex:
            log.error("Error : {}".format(ex))
    
    def handle_publish_internal_client(self):
        log.info("Starting handle internal client publish...")

        lock = self.get_lock(self.internal_client_mutex_id)
        lock_message = self.get_lock(self.message_mutex_id)

        while self.do_running:
            with lock:
                if not self.internal_clients:
                    continue

                for internal_client in self.internal_clients:
                    message = ""
                    with lock_message:
                        if not self.messages.has_message_topic(internal_client):
                            continue

                        if self.messages.empty_message(internal_client):
                            continue

                        message = self.messages.get_message(internal_client)
                    
                    if not message:
                        continue

                    self.internal_clients[internal_client].publish(message)
                    self.sleep(0.0001)
            
            self.sleep(1)

    def event(self,host,port,event):
        name = "{}:{}".format(host,port)
        my_server_name = self.get_server_name()
        if (event == JOINED_SERVER) and (name != my_server_name):
            self.new_internal_client(host,port)
        elif (event == DISCONNECT_SERVER):
            self.sub_internal_client(name)
        elif (event == GET_CLUSTER) and (name != my_server_name):
            self.publish_resp_cluster_server()
        elif (event == RESP_CLUSTER) and (name != my_server_name):
            self.new_internal_client(host,port)
            
    def handle_event(self,payload):
        try:
            data = payload["data"]
            if type(data) in [bytes]:
                data = data.decode()
                json_data = string_to_json(data)
                self.event(json_data['host'],json_data['port'],json_data['event'])
        except ValueError as ve:
            log.error("Handle event value error : {}".format(ve))
        except KeyError as ke:
            log.error("Handle event key error : {}".format(ke))
        except Exception as ex:
            log.error("Handle error : {}".format(ex))
        
    def handle_redis_subscribe(self):
        log.info("Starting redis subscriber...")
        while self.do_running:
            lock = self.get_lock(self.redis_subscriber_mutex_id)
            with lock:
                payload = self.redis_subscriber.get_payload()
                if payload is None:
                    continue

                self.handle_event(payload)
            
            self.sleep(5)
    
    def publish_join_server(self):
        lock = self.get_lock(self.redis_publisher_mutex_id)
        with lock:
            if self.redis_publisher is not None:
                payload = publish_payload(self.host,self.port,JOINED_SERVER)
                self.redis_publisher.publish(self.topic,json_to_string(payload))
                log.info("Publish join new server -> {}:{} successed".format(self.host,self.port))
    
    def publish_disconnect_server(self):
        lock = self.get_lock(self.redis_publisher_mutex_id)
        with lock:
            if self.redis_publisher is not None:
                payload = publish_payload(self.host,self.port,DISCONNECT_SERVER)
                self.redis_publisher.publish(self.topic,json_to_string(payload))
                log.info("Publish disconnect server -> {}:{} successed".format(self.host,self.port))

    def publish_get_cluster_server(self):
        lock = self.get_lock(self.redis_publisher_mutex_id)
        with lock:
            if self.redis_publisher is not None:
                payload = publish_payload(self.host,self.port,GET_CLUSTER)
                self.redis_publisher.publish(self.topic,json_to_string(payload))
                log.info("Publish get list server -> {}:{} successed".format(self.host,self.port))
    
    def publish_resp_cluster_server(self):
        lock = self.get_lock(self.redis_publisher_mutex_id)
        with lock:
            if self.redis_publisher is not None:
                payload = publish_payload(self.host,self.port,RESP_CLUSTER)
                self.redis_publisher.publish(self.topic,json_to_string(payload))
                log.info("Publish response server -> {}:{} successed".format(self.host,self.port))
    
    def sleep(self,sec=1):
        time.sleep(sec)

    def run(self):
        log.info("Start server : {}:{}".format(self.host,self.port))

        self.sleep(1)
        thread = threading.Thread(target=self.handle_redis_subscribe,args=())
        thread.setDaemon(True)
        thread.start()

        self.sleep(1)
        self.publish_join_server()

        self.sleep(1)
        self.publish_get_cluster_server()

        self.sleep(1)
        thread = threading.Thread(target=self.handle_publish_internal_client,args=())
        thread.setDaemon(True)
        thread.start()

        self.sleep(1)
        thread = threading.Thread(target=self.handle_notify_client,args=())
        thread.setDaemon(True)
        thread.start()
        
        self.sleep(1)
        self.handle_accept()
    
    def disconnect_internal_client(self):
        lock = self.get_lock(self.internal_client_mutex_id)
        with lock:
            if not self.internal_clients:
                return
            
            for internal_client in self.internal_clients:
                self.internal_clients[internal_client].close()
                del self.internal_clients[internal_client]
            
            log.info("Disconnect internal clients successed")

    def close(self):
        self.disconnect_internal_client()
        self.sleep(2)
        self.publish_disconnect_server()
        self.sock.close()
        log.info("Server -> {}:{} has closed".format(self.host,self.port))

if __name__ == "__main__":
    parser.add_argument("-u", "--url", help = "Server host ",default='127.0.0.1')
    parser.add_argument("-p", "--port", help = "Server port",default=5000)
    args = parser.parse_args()
    server = Server(host=args.url,port=int(args.port))
    try:
        server.run()
    except KeyboardInterrupt:
        log.info("Stop server..")
        server.close()
        sys.exit()