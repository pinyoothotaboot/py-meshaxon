import sys
import socket
import time
import threading
from lib.event import *
from lib.parse import *

class InternalClient:
    def __init__(self,host = "127.0.0.1",port = 4000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.do_runing = True
        self.BUFFER_SIZE = 2048
        self.count = 0
        self.user_id = ""
        self.connect()
    
    def get_hostname(self):
        return "{}:{}".format(self.host,self.port)
    
    def get_sock(self):
        return self.sock

    def connect(self):
        try:
            self.sock.connect((self.host,self.port))
        except socket.error as e:
            print(str(e))
    
    def handle_recieve(self):
        while self.do_runing:
            resp = self.sock.recv(self.BUFFER_SIZE)
            if resp:
                print("{} :Received data : {}\n\r".format(self.count,resp.decode()))
                self.count+=1
            
            time.sleep(0.5)

    def handle_send(self):
        while self.do_runing:
            data = input('{}:{}>'.format(self.host,self.port))
            if data:
                print("Send data : {}\r".format(data))
                self.sock.send(data.encode())
            time.sleep(0.2)
    
    def pack_command(self,event,payload):
        return "<{}<>{}>".format(event,json_to_string(payload))
    
    def add_user(self,user_id):
        self.user_id = user_id
    
    def get_user(self):
        return self.user_id

    def publish(self,cmd):
        self.sock.sendall(cmd.encode())

    def join_lobbie(self):
        cmd = self.pack_command(
            EVENT_JOIN_LOBBIE,
            {
                "user_id" : self.get_user(),
                "host" : self.get_hostname()
            }
        )
        self.publish(cmd)

    def send_message(self,to_user_id,message):
        cmd = self.pack_command(
            EVENT_SEND_MASSAGE_TO_USER,
            {
                "to" : to_user_id,
                "from" : self.get_user(),
                "message" : message
            }
        )
        self.publish(cmd)
        
    def run(self):
        print("Connect to : {}:{}".format(self.host,self.port))
        thread = threading.Thread(target=self.handle_recieve)
        thread.setDaemon(True)
        thread.start()

        self.handle_send()

    def close(self):
        self.sock.close()
        print("Disconnect socket client user id : {}".format(self.user_id))

if __name__ == "__main__":
    client = InternalClient(host="127.0.0.1",port=4000)
    try:
        client.add_user("user_01")
        client.join_lobbie()
    
        #client.send_message("user_01","Hello user 01")

        client.run()
    except KeyboardInterrupt:
        print("Stop process..")
        client.close()
        sys.exit()