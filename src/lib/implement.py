from re import T
from .event import *
from .parse import *

def cmd_packet(event,payload):
    return "<{}<>{}>".format(event,json_to_string(payload))

def join_lobbie(payload,messages,lock_message,user,lock_user,connection,internal_clients,lock_internal):
    try:
        user_id = payload["user_id"]
        host = payload["host"]

        with lock_user:
            user.add_user(user_id,host,connection.get_name())
        
        payload['sock_name'] = connection.get_name()
        cmd = cmd_packet(EVENT_SERVER_JOIN_LOBBIE,payload)

        with lock_internal:
            for internal_client in internal_clients:
                if host == internal_client:
                    continue

                with lock_message:
                    messages.add_message(internal_client,cmd)
        
        connection.set_username(user_id)
        connection.notify(f"Join user id : {user_id} successed")
    except ValueError as ve:
        print("Value error : {}".format(ve))
        connection.notify(f"Not found value of payload!.")
    except KeyError as ke:
        print("Key error : {}".format(ke))
        connection.notify(f"Not found key of payload!.")

def add_user_to_lobbie(payload,user,lock_user):
    try:
        user_id = payload["user_id"]
        host = payload["host"]
        sock_name = payload['sock_name']

        with lock_user:
            user.add_user(user_id,host,sock_name)

    except ValueError as ve:
        print("Value error : {}".format(ve))
    except KeyError as ke:
        print("Key error : {}".format(ke))

def publish_message(payload,messages,lock_message,user,lock_user,database,lock_database,connection):
    try:
        to_user_id = payload['to']
        from_user_id = payload['from']

        to_host_user = ""
        from_host_user = ""

        with lock_user:
            to_host_user = user.get_user_host(to_user_id)
            from_host_user = user.get_user_host(from_user_id)
        
        if not to_host_user and not from_host_user:
            return
        
        if to_host_user == from_host_user:
            with lock_database:
                cmd = cmd_packet(EVENT_RECIEVE_MESSAGE_FROM_USER,payload)
                database.publish(to_user_id,cmd)
        else:
            with lock_message:
                cmd = cmd_packet(EVENT_SERVER_SEND_MASSAGE_TO_USER,payload)
                messages.add_message(to_host_user,cmd)

    except ValueError as ve:
        print("Value error : {}".format(ve))
        connection.notify(f"Not found value of payload!.")
    except KeyError as ke:
        print("Key error : {}".format(ke))
        connection.notify(f"Not found key of payload!.")

def send_message_to_user(payload,database,lock_database):
    try:
        to_user_id = payload['to']

        with lock_database:
            cmd = cmd_packet(EVENT_RECIEVE_MESSAGE_FROM_USER,payload)
            database.publish(to_user_id,cmd)

    except ValueError as ve:
        print("Value error : {}".format(ve))
    except KeyError as ke:
        print("Key error : {}".format(ke))