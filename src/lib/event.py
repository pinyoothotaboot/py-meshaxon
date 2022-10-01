VERSION_1 = "v1"
LEVEL_ROOM = "room"
LEVEL_APP = "app"
LEVEL_PEER = "peer"
LEVEL_SERVER = "server"

EMIT = "emit"
ON = "on"

# Client -> Server
EVENT_JOIN_LOBBIE = "{}:{}:{}:join_lobbie".format(VERSION_1,EMIT,LEVEL_APP)
EVENT_BROADCAST_LOBBIE   = "{}:{}:{}:broadcast_lobbie".format(VERSION_1,EMIT,LEVEL_APP)
EVENT_JOIN_ROOM   = "{}:{}:{}:join_room".format(VERSION_1,EMIT,LEVEL_APP)
EVENT_CREATE_ROOM   = "{}:{}:{}:create_room".format(VERSION_1,EMIT,LEVEL_APP)
EVENT_SEND_MASSAGE_TO_ROOM   = "{}:{}:{}:send_message_to_room".format(VERSION_1,EMIT,LEVEL_APP)
EVENT_SEND_MASSAGE_TO_USER   = "{}:{}:{}:send_message_to_user".format(VERSION_1,EMIT,LEVEL_APP)

# Server -> CLient
EVENT_RECIEVE_MESSAGE_FROM_ROOM   = "{}:{}:{}:recieve_message_from_room".format(VERSION_1,ON,LEVEL_ROOM)
EVENT_RECIEVE_MESSAGE_FROM_USER   = "{}:{}:{}:recieve_message_from_user".format(VERSION_1,ON,LEVEL_PEER)

# Server -> Server
EVENT_SERVER_JOIN_LOBBIE = "{}:{}:{}:join_lobbie".format(VERSION_1,EMIT,LEVEL_SERVER)
EVENT_SERVER_BROADCAST_LOBBIE   = "{}:{}:{}:broadcast_lobbie".format(VERSION_1,EMIT,LEVEL_SERVER)
EVENT_SERVER_SEND_MASSAGE_TO_USER   = "{}:{}:{}:send_message_to_user".format(VERSION_1,ON,LEVEL_SERVER)