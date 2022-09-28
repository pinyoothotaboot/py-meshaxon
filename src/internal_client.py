import sys
import socket
import time
import threading

class InternalClient:
    def __init__(self,host = "127.0.0.1",port = 4000,database = None,database_lock = None , message_queue = None , message_lock = None):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.do_runing = True
        self.BUFFER_SIZE = 2048
        self.count = 0
        self.TYPE_CLIENT = "INTERNAL"
        self.connect()
    
    def get_name(self):
        return "{}:{}".format(self.host,self.port)
    
    def get_sock(self):
        return self.sock
    
    def get_type(self):
        return self.TYPE_CLIENT

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
            
            time.sleep(0.2)

    def handle_send(self):
        while self.do_runing:
            data = input('{}:{}>'.format(self.host,self.port))
            if data:
                print("Send data : {}\r".format(data))
                self.sock.send(data.encode())
            time.sleep(0.2)
    
    def publish(self,payload):
        try:
            if payload:
                self.sock.sendall(payload.encode())
        except Exception as ex:
            pass
    
    def verify_internal(self):
        self.sock.sendall(self.get_type().encode())
        
    def run(self):
        print("Connect to : {}:{}".format(self.host,self.port))
        self.verify_internal()
    
    def close(self):
        if self.sock:
            self.sock.close()
            
if __name__ == "__main__":
    try:
        client = InternalClient()
        client.run()
    except KeyboardInterrupt:
        print("Stop process..")
        sys.exit()