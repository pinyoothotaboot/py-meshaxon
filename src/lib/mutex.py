import uuid
from threading import Lock

class Mutex:
    def __init__(self):
        self.id = uuid.uuid1()
        self.locks = dict()
        self.lock = Lock()
    
    """
        Function : lock_id
        @sync
        About : Generate mutex id
        Param :
            - String : key
    """
    def lock_id(self,key = "") -> str:
        return "{}-{}".format(key,self.id)

    """
        Function : add_lock
        @sync
        About : Create new lock and store
        Param :
            - String : key
    """
    def add_lock(self,key="") -> None:
        if not key:
            return

        mutex_id = self.lock_id(key)
        self.lock.acquire()

        if mutex_id not in self.locks:
            self.locks[mutex_id] = Lock()

        self.lock.release()
    
    """
        Function : get_lock
        @sync
        About : Get lock by key
        Param :
            - String : key
        Return :
            Lock
    """
    def get_lock(self,key=""):
        if not key:
            return
        
        mutex_id = self.lock_id(key)
        self.lock.acquire()
        lock = None

        if mutex_id in self.locks:
            lock = self.locks[mutex_id]
        self.lock.release()

        return lock
    
    """
        Function : delete_lock
        @sync
        About : Delete lock by key
        Param :
            - String : key
    """
    def delete_lock(self,key=""):
        if not key:
            return
        
        mutex_id = self.lock_id(key)
        self.lock.acquire()
        if mutex_id in self.locks:
            del self.locks[mutex_id]
        
        self.lock.release()