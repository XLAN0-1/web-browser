from datetime import datetime

class BrowserCache:
    def __init__(self):
        self.storage = {}
        self.time_added = {}


    def add_to_cache_age(self, uri, age, body):
        self.storage[uri] = body
        self.timeAdded[uri] = (age, datetime.now().timestamp())

    def remove_from_cache(self, uri):
        if uri in self.storage:
            del self.storage[uri]

        if uri in self.timeAdded:
            del self.time_added[uri]

        return True

    def is_expired(self, uri):
        if uri in self.time_added:
            val = self.time_added[uri]

            if val[0] + val[1] > datetime.now().timestamp():
                self.remove_from_cache(uri)
                return True
            
            return False
        
        return True

    def get_cache_item(self, uri):
        if not self.is_expired(uri):
            return self.storage[uri]
        return -1