import json
import base64

class Converter:
    @staticmethod
    def encode(data):
        json_string = json.dumps(data)
        return base64.b64encode(json_string.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode(base64_string, utf=True):
        decoded = base64.b64decode(base64_string)
        return json.loads(decoded.decode("utf-8")) if utf else decoded