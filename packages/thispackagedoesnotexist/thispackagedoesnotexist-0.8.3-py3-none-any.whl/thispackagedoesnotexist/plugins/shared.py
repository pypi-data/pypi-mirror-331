import time

class SharedData:
    def __init__(self, ):
        self.data = {}

    def set_data(self, identifier, value):
        self.data[identifier] = value

    def get_data(self, identifier):
        return self.data.pop(identifier, None)
    
    def get_shared_data(self, *keys):
        shared_data = None

        for key in keys:
            shared_data = self.get_data(key)
            if shared_data:
                return shared_data