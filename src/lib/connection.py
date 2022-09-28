import uuid

class Connection:
    def __init__(self,socket = None,addr = None) -> None:
        self.id = uuid.uuid1()
        self.socket = socket
        self.name = self.socket.fileno()
        self.address = addr
        self.my_host = ""
        self.type_name = "EXTERNAL"
        self.user_name = ""

    """
        Function : get_name
        @sync
        About : Get connection name
        Return :
            - name
    """
    def get_name(self):
        return self.name
    
    def get_sock(self):
        return self.socket
    
    def get_address(self):
        return "{}:{}".format(self.address[0],self.address[1])
    
    def add_my_host(self,host):
        self.my_host = host
    
    def get_my_host(self):
        return self.my_host
    
    def set_type(self,type_name):
        self.type_name = type_name
    
    def get_type(self):
        return self.type_name

    def set_username(self,user_name):
        self.user_name = user_name
    
    def get_username(self):
        return self.user_name

    """
        Function : notify
        @sync
        About : Notify payload to client
        Param :
            - String : payload
    """
    def notify(self,payload = ""):
        if not payload:
            return
        
        self.socket.sendall(payload.encode())