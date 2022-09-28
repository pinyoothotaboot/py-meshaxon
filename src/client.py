import sys
import socket
import time
import threading

class InternalClient:
    def __init__(self,host = "127.0.0.1",port = 5000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.do_runing = True
        self.BUFFER_SIZE = 2048
        self.count = 0
        self.connect()
    
    def get_name(self):
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
        
    def run(self):
        print("Connect to : {}:{}".format(self.host,self.port))
        thread = threading.Thread(target=self.handle_recieve)
        thread.setDaemon(True)
        thread.start()

        self.handle_send()

if __name__ == "__main__":
    try:
        client = InternalClient()
        client.run()
    except KeyboardInterrupt:
        print("Stop process..")
        sys.exit()