from .parse import string_to_json

def validate_pattern(data):
    if "<" != data[0] and ">" != data[-1] and "<>" not in data:
        return False
    
    return True

def split_data(data):
    data = data[1:-1]
    data = data.split("<>")

    return data[0],data[1]

"""
    Pattern : <EVENT<>Payload>
"""
def handle_recieve_event(data):
    if not validate_pattern(data):
        return "",{}

    event,payload = split_data(data)

    payload = string_to_json(payload)
    if not payload:
        return "",{}
    
    return event,payload