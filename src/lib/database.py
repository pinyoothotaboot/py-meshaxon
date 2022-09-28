import sys
import os
sys.path.append(os.getcwd())
import uuid
from .mutex import Mutex
from typing import List,Dict
from .store.db_hashmap import DbHashMap
from .store.db_queue import DbQueue
from .store.db_stack import DbStack

class Database:
    def __init__(self):
        self.id = uuid.uuid1()
        self.stacks = dict()
        self.queues = dict()
        self.hashmaps = dict()
        self.lock = Mutex()

        self.stack_id = "stacks-{}".format(self.id)
        self.queue_id = "queues-{}".format(self.id)
        self.hashmap_id = "hashmaps-{}".format(self.id)

        self.initial_lock()

    """
        Function : initial_lock
        @sync
        About : Initial mutex
    """
    def initial_lock(self):
        self.lock.add_lock(self.stack_id)
        self.lock.add_lock(self.queue_id)
        self.lock.add_lock(self.hashmap_id)
    
    """
        Function : get_lock
        @sync
        About : Get mutex lock
        Param :
            - String : id
        Return :
            - lock
    """
    def get_lock(self,id = ""):
        return self.lock.get_lock(id)

    """
        Function : get
        @sync
        About : Get data by key from topic stack 
        Param :
            - String : topic
            - String : key
        Return :
            - data
    """
    def get(self,topic ="",key="") -> str:
        if not topic or not key:
            return ""
        
        data = ""
        lock = self.get_lock(self.hashmap_id)
        lock.acquire()
        if topic in self.hashmaps:
            hashmap = self.hashmaps[topic]
            data = hashmap.get(key)
        
        lock.release()

        return data

    """
        Function : set
        @sync
        About : Set data by key and create/update topic
        Param :
            - String : topic
            - String : key
            - String : value
            - Boolean : has_dubplicate = True
    """
    def set(self,topic = "",key="",value="",has_dubplicate = True):
        if not topic or not key:
            return
        
        lock = self.get_lock(self.hashmap_id)
        lock.acquire()
        if topic not in self.hashmaps:
            hashmap = DbHashMap()
            hashmap.add_dubplicate(key,value)
            self.hashmaps[topic] = hashmap
        else:
            if has_dubplicate:
                self.hashmaps[topic].add_dubplicate(key,value)
            else:
                self.hashmaps[topic].add_replace(key,value)
        lock.release()

    """
        Function : push
        @sync
        About : Push data to stack by topic
        Param :
            - String : topic
            - String : data
    """
    def push(self,topic = "",data=""):
        if not topic:
            return
        
        lock = self.get_lock(self.stack_id)
        lock.acquire()
        if topic not in self.stacks:
            stack = DbStack()
            stack.add(data)
            self.stacks[topic] = stack
        else:
            self.stacks[topic].add(data)
        lock.release()

    """
        Function : pop
        @sync
        About : Pop data from stack by topic
        Param :
            - String : topic
        Return :
            - data
    """
    def pop(self,topic = "") -> str:
        if not topic:
            return ""
        
        data = ""
        lock = self.get_lock(self.stack_id)
        lock.acquire()
        if topic in self.stacks:
            stack = self.stacks[topic]
            data = stack.peek()
        lock.release()

        return data

    """
        Function : list
        @sync
        About : List datas from stack by topic
        Param :
            - String : topic
            - Int : start
            - Int : stop
        Return :
            - datas
    """
    def list(self,topic ="",start=0,stop=-1) -> List:
        if not topic:
            return []
        
        datas = []
        lock = self.get_lock(self.stack_id)
        lock.acquire()
        if topic in self.stacks:
            stack = self.stacks[topic]
            datas = stack.range(start,stop)
        lock.release()
        
        return datas

    """
        Function : publish
        @sync
        About : Publish data to subscribers
        Param :
            - String : topic
            - String : data
    """
    def publish(self,topic="",data=""):
        if not topic:
            return
        
        lock = self.get_lock(self.queue_id)
        lock.acquire()
        if topic not in self.queues:
            queue = DbQueue()
            queue.add(data)
            self.queues[topic] = queue
        else:
            self.queues[topic].add(data)
        lock.release()

    """
        Function : subscribe
        @sync
        About : Subscribe data from publisher
        Param :
            - String : topic
        Return :
            - data
    """
    def subscribe(self,topic = "") -> str:
        if not topic:
            return ""
        
        data = ""
        lock = self.get_lock(self.queue_id)
        lock.acquire()
        if topic in self.queues:
            queue = self.queues[topic]
            data = queue.get()
        lock.release()
        return data

    """
        Function : clear
        @sync
        About : Clear datas and new 
    """
    def clear(self):
        
        lock_queue = self.get_lock(self.queue_id)
        with lock_queue:
            self.queues = None
            self.queues = dict()
        
        lock_stack = self.get_lock(self.stack_id)
        with lock_stack:
            self.stacks = None
            self.stacks = dict()
        
        lock_hashmap = self.get_lock(self.hashmap_id)
        with lock_hashmap:
            self.hashmaps = None
            self.hashmaps = dict()