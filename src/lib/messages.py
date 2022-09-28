from .store.db_queue import DbQueue
from .mutex import Mutex

class Messages:

    def __init__(self):
        self.messages = dict()
        self.message_lock = Mutex()
        self.message_mutex_id = "messages"

        self.initial_lock()
    
    def initial_lock(self):
        self.message_lock.add_lock(self.message_mutex_id)
    
    def get_lock(self,mutex_id):
        return self.message_lock.get_lock(mutex_id)

    def add_message(self,topic,payload):
        lock = self.get_lock(self.message_mutex_id)
        with lock:
            if topic not in self.messages:
                queue = DbQueue()
                queue.add(payload)
                self.messages[topic] = queue
            else:
                self.messages[topic].add(payload)
    
    def has_message_topic(self,topic):
        lock = self.get_lock(self.message_mutex_id)
        with lock:
            if topic in self.messages:
                return True
        return False
    
    def empty_message(self,topic):
        lock = self.get_lock(self.message_mutex_id)
        with lock:
            if topic in self.messages:
                return self.messages[topic].is_empty()
        return None
    
    def get_message(self,topic):
        lock = self.get_lock(self.message_mutex_id)
        with lock:
            if topic in self.messages:
                return self.messages[topic].get()
        return ""
    
    def delete_message_topic(self,topic):
        lock = self.get_lock(self.message_mutex_id)
        with lock:
            if topic in self.messages:
                del self.messages[topic]
    

