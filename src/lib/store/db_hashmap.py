import sys
import os
sys.path.append(os.getcwd())
import uuid
from typing import Dict,List
from ..mutex import Mutex

class DbHashMap:
    def __init__(self,name=uuid.uuid1()):
        self.name = name
        self.hash = dict()
        self.lock = Mutex()
        self.lock.add_lock("hash-{}".format(self.name))
    
    """
        Function : get_name
        @sync
        About : Get hashmap name
        Return :
            - name
    """
    def get_name(self) -> str:
        return self.name
    
    """
        Function : get_lock
        @sync
        About : Get mutex of hashmap
    """
    def get_lock(self):
        return self.lock.get_lock("hash-{}".format(self.name))
    
    """
        Function : is_empty
        @sync
        About : Check data in stack
        Return : 
            - True/False
    """
    def is_empty(self) -> bool:
        status = False
        status = len(self.hash) == 0
        return status
    
    """
        Function : add_dubplicate
        @sync
        About : Add value to hashmap by key with dubplicate value in array
        Param :
            - String : key
            - String : value
        Return :
            - True/False
    """
    def add_dubplicate(self,key="",value="") -> bool:
        if not key:
            return False
        
        status = False
        if key not in self.hash:
            self.hash[key] = [value]
        else:
            self.hash[key].append(value)
        status = True

        return status
    
    """
        Function : add_replace
        @sync
        About : Add value to hashmap by key with replace value in array
        Param :
            - String : key
            - String : value
        Return :
            - True/False
    """
    def add_replace(self,key="",value="") -> bool:
        if not key:
            return False
        
        status = False
        if key not in self.hash:
            self.hash[key] = [value]
        else:
            self.hash[key] = [value]
        status = True

        return status
    
    """
        Function : get
        @sync
        About : Get value from hashmap by key
        Param :
            - String : key
        Return :
            - value
    """
    def get(self,key="") -> List:
        if not key:
            return []
        
        value = []
        if key in self.hash:
            value = self.hash[key]

        return value
    
    """
        Function : drop
        @sync
        About : Drop value in hashmap by key
        Param :
            - String : key
        Return :
            - value
    """
    def drop(self,key="") -> bool:
        if not key:
            return False
        
        status = False
        if key in self.hash:
            del self.hash[key]
        status = True

        return status
    
    """
        Function : clear
        @sync
        About : Clear datas in hashmap
    """
    def clear(self):
        self.hash = dict()

