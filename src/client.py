import sys
import socket
import time,datetime
import threading
import argparse
from lib.event import *
from lib.parse import *
from lib.handle import *
from lib.e2e import *
from lib.log import *

parser = argparse.ArgumentParser()

log = Logger('CLIENT').get_logger()

class Client:
    def __init__(self,host = "127.0.0.1",port = 4000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.do_runing = True
        self.BUFFER_SIZE = 2048
        self.count = 0
        self.user_id = ""
        self.e2e = EndToEndEncrypt()

        self.connect()
    
    def get_hostname(self):
        return "{}:{}".format(self.host,self.port)
    
    def get_sock(self):
        return self.sock

    def connect(self):
        try:
            self.sock.connect((self.host,self.port))
        except socket.error as e:
            log.error("Socket error : {}".format(e))
    
    def encrypt(self,payload):
        try:
            salt = self.e2e.get_salt()
            key = self.e2e.get_key(payload,salt)
            enc_message = self.e2e.encrypt(payload['message'],key)
            enc_payload = self.e2e.payload(enc_message.decode(),salt)
            return enc_payload
        except KeyError as ke:
            log.error("Key error : {}".format(ke))
            return {}
        except ValueError as ve:
            log.error("Value error : {}".format(ve))
            return {}
    
    def decrypt(self,payload):
        try:
            salt = payload['message']['salt']
            key = self.e2e.get_key(payload,salt)
            dec_message = self.e2e.decrypt(payload['message']['enc_message'],key)
            payload['message'] = dec_message
            return payload
        except KeyError as ke:
            log.error("Key error : {}".format(ke))
            return {}
        except ValueError as ve:
            log.error("Value error : {}".format(ve))
            return {}

    def display_message(self,payload):
        try:
            from_user = payload['from']
            message = payload['message']
            print("\n{} say : {}\r".format(from_user,message))
        except KeyError as ke:
            log.error("Key error : {}".format(ke))
        except ValueError as ve:
            log.error("Value error : {}".format(ve))

    def handle_event(self,resp):
        event,payload = handle_recieve_event(resp.decode())
        if event == EVENT_RECIEVE_MESSAGE_FROM_USER:
            payload = self.decrypt(payload)
            self.display_message(payload)
    
    def handle_recieve(self):
        while self.do_runing:
            resp = self.sock.recv(self.BUFFER_SIZE)
            if resp:
                self.handle_event(resp)
            
            self.sleep(0.5)

    def handle_send(self):
        while self.do_runing:
            data = input('[{}]{}>'.format(self.get_user(),self.get_hostname()))
            if data:
                print("\nSend data : {}\r".format(data))
                self.sock.send(data.encode())

            self.sleep(0.2)
    
    def pack_command(self,event,payload):
        return "<{}<>{}>".format(event,json_to_string(payload))
    
    def add_user(self,user_id):
        self.user_id = user_id
    
    def get_user(self):
        return self.user_id

    def publish(self,cmd):
        self.sock.sendall(cmd.encode())

    def subscribe(self):
        resp = self.sock.recv(self.BUFFER_SIZE)
        if resp:
            event,payload = handle_recieve_event(resp.decode())
            if event == EVENT_RECIEVE_MESSAGE_FROM_USER:
                payload = self.decrypt(payload)
                return payload

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
        raw_payload = {
            "to" : to_user_id,
            "from" : self.get_user(),
            "message" : message
        }

        enc_payload = self.encrypt(raw_payload)
        
        raw_payload['message'] = enc_payload
        cmd = self.pack_command(
            EVENT_SEND_MASSAGE_TO_USER,
            raw_payload
        )

        self.publish(cmd)
        
    def run(self):
        log.info("Connect to : {}:{}".format(self.host,self.port))
        thread = threading.Thread(target=self.handle_recieve)
        thread.setDaemon(True)
        thread.start()

        self.handle_send()
    
    def sleep(self,ms=0.2):
        time.sleep(ms)

    def close(self):
        self.sock.close()
        log.info("Disconnect socket client user id : {}".format(self.user_id))

if __name__ == "__main__":
    parser.add_argument("-u", "--url", help = "Client connect host ",default='127.0.0.1')
    parser.add_argument("-p", "--port", help = "Client connect port",default=5000)
    parser.add_argument("-n", "--username", help = "User name",default="user_01")
    args = parser.parse_args()

    client = Client(host=args.url,port=int(args.port))
    try:
        client.add_user(args.username)
        client.join_lobbie()
        #client.send_message("pinyoo","Hello Pinyoo")
        client.run()
    except KeyboardInterrupt:
        log.debug("Stop process..")
        client.close()
        sys.exit()