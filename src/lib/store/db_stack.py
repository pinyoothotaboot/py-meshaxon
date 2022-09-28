from inspect import stack
import sys
import os
sys.path.append(os.getcwd())
import uuid
from typing import List
from ..mutex import Mutex

class DbStack:
    def __init__(self,name = uuid.uuid1()):
        self.name = name
        self.stack = []
        self.lock = Mutex()
        self.lock.add_lock("stack-{}".format(self.name))
    
    """
        Function : get_name
        @sync
        About : Get stack name
        Return :
            - name
    """
    def get_name(self) -> str:
        return self.name
    
    """
        Function : get_lock
        @sync
        About : Get mutex of stack
    """
    def get_lock(self):
        return self.lock.get_lock("stack-{}".format(self.name))
    
    """
        Function : is_empty
        @sync
        About : Check data in stack
        Return : 
            - True/False
    """
    def is_empty(self) -> bool:
        status = False
        status = len(self.stack) == 0
        return status
    
    """
        Function : add
        @sync
        About : Add data to stack
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
        self.stack.append(data)
        status = True
        return status
    
    """
        Function : peek
        @sync
        About : See first data of stack
        Return :
            - data
    """
    def peek(self) -> str:
        if self.is_empty():
            return ""
        
        data = ""
        data = self.stack[-1]
        return data
    
    """
        Function : pop
        @sync
        About : Get first data of stack and pop
        Return :
            - data
    """
    def pop(self) -> str:
        if self.is_empty():
            return ""
        
        data = ""
        data = self.stack[-1]
        self.stack.pop(-1)
        return data
    
    """
        Function : range
        @sync
        About : List datas of stack
        Param :
            - Int : start
            - Int : stop
        Return :
            - datas
    """
    def range(self,start=0,stop=-1) -> List:
        if self.is_empty():
            return []
        
        if not (start.isdigit() and stop.isdigit()):
            return []
        
        start = int(start) if int(start) < len(self.stack) else 0
        stop = int(stop) if (int(stop) > start) and (int(stop) < len(self.stack)) else -1
        
        datas = []
        datas = self.stack[start:stop]
        return datas
    
    """
        Function : clear
        @sync
        About : Clear data in stack
    """
    def clear(self):
        self.stack = []
