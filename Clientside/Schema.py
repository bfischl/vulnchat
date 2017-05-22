from jsonschema import validate
from jsonschema import ValidationError

command = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "command",
    "type": "object",
    "properties": {
        "id": {
          "description": "The unique identifier for this command",
          "type": "integer"
        },
        "time": {
            "description": "The time, in seconds, from when this event is loaded until this command is executed",
            "type": "number",
            "minimum": 0,
        },
        "target":{
            "description": "The sub-section of the exercise this command will target",
            "type": "string",
        },
        "calltask":{
            "description": "The function to be called by the target subsystem, identified above",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "parameters": {"type": "array",
                               "items": {
                                   "type": "string"
                               }
                               }
            }


        }
    }
}


def is_valid_command(tmp_command):
    try :
        validate(tmp_command, command)
        return True
    except ValidationError:
        return False



print is_valid_command({"id":1,"time":10,"target":"vulnchat","calltask":{"name": "send_message","parameters":["test",]}})