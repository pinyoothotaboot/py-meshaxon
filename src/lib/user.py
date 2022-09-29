from .mutex import Mutex
from .log import Logger

log = Logger('USER').get_logger()

class User:
    def __init__(self) -> None:
        self.users = dict()
        self.user_lock = Mutex()
        self.user_mutex_id = "user"
        self.initial_lock()
    
    def initial_lock(self):
        self.user_lock.add_lock(self.user_mutex_id)
    
    def get_lock(self,mutex_id):
        return self.user_lock.get_lock(mutex_id)
    
    def add_user(self,user_id,server_host,sock_name):
        lock = self.get_lock(self.user_mutex_id)
        with lock:
            if user_id not in self.users:
                user = {
                    "host" : server_host,
                    "user_id" : user_id,
                    "sock_name" : sock_name
                }
                self.users[user_id] = user
                log.info("Add new user id : {} successed".format(user_id))
            else:
                self.users[user_id]["host"] = server_host
                self.users[user_id]["sock_name"] = sock_name
                log.info("Update user id : {} successed".format(user_id))

    def delete_user(self,user_id):
        lock = self.get_lock(self.user_mutex_id)
        with lock:
            if user_id in self.users:
                del self.users[user_id]
                log.info("Delete user id : {} successed".format(user_id))

    def has_user(self,user_id):
        lock = self.get_lock(self.user_mutex_id)
        with lock:
            if user_id in self.users:
                return True
        return False
    
    def get_user_host(self,user_id):
        lock = self.get_lock(self.user_mutex_id)
        with lock:
            if user_id in self.users:
                return self.users[user_id]["host"]
        return ""
    
    def get_user_sock(self,user_id):
        lock = self.get_lock(self.user_mutex_id)
        with lock:
            if user_id in self.users:
                return self.users[user_id]["sock_name"]
        return ""
    
    def close(self):
        lock = self.get_lock(self.user_mutex_id)
        with lock:
            self.users = dict()
            log.debug("Close all user")