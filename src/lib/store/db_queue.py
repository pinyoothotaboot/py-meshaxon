import sys
import os
sys.path.append(os.getcwd())
from queue import Queue
from ..mutex import Mutex
import uuid

class DbQueue:
    def __init__(self,name = uuid.uuid1()):
        self.name = name
        self.lock = Mutex()
        self.queue = []
        self.lock.add_lock("queue-{}".format(self.name))
    
    """
        Function : get_name
        @sync
        About : Get name of queue
        Return :
            - name
    """
    def get_name(self) -> str:
        return self.name
    
    """
        Function : get_lock
        @sync
        About : Get mutex lock
        Return :
            - lock
    """
    def get_lock(self):
        return self.lock.get_lock("queue-{}".format(self.name))
    
    """
        Function : is_empty
        @sync
        About : Check empty queue
        Return :
            - True/False
    """
    def is_empty(self) -> bool:
        return len(self.queue) == 0
    
    """
        Function : add
        @sync
        About : Add data to queue
        Param :
            - String : data
        Return : 
            - True/False
    """
    def add(self,data="") -> bool:
        if not data:
            return False
        
        if not isinstance(data,str):
            return False

        status = False
        self.queue.append(data)
        status = True
        return status
    
    """
        Function : get
        @sync
        About : Get data from queue and pop
        Return :
            - data
    """
    def get(self) -> str:
        data = ""
        if not self.is_empty():
            data = self.queue.pop(0)
        return data
    
    """
        Function : clear
        @sync
        About : Clear data in queue
    """
    def clear(self):
        self.queue = []
            
