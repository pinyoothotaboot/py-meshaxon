import json

def json_to_string(payload):
    if not payload:
        return ""

    try:
        return json.dumps(payload)
    except:
        return ""

def string_to_json(string):
    if not string:
        return {}
    
    try:
        return json.loads(string)
    except ValueError:
        return {}

def publish_payload(host,port,event):
    return {
        "host" : host,
        "port" : port,
        "event" : event
    }

"""
    {
        "type" : "PUBLISH/BROADCAST/CMD",
        "payload" : {
            "command": "JOIN/CREATE/",
            
        }
    }
"""