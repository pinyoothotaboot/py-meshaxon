from .constant import *
from .event import *
from .implement import *

def usecase_command(event,payload,messages,lock_message,database,lock_database,user,lock_user,connection,internal_clients,lock_internal,connections):

    if event == EVENT_JOIN_LOBBIE:
        join_lobbie(payload,messages,lock_message,user,lock_user,connection,internal_clients,lock_internal)
    
    elif event == EVENT_SERVER_JOIN_LOBBIE:
        add_user_to_lobbie(payload,user,lock_user)
    
    elif event == EVENT_SEND_MASSAGE_TO_USER:
        publish_message(payload,messages,lock_message,user,lock_user,database,lock_database,connection)
    
    elif (event == EVENT_SERVER_SEND_MASSAGE_TO_USER):
        send_message_to_user(payload,database,lock_database)