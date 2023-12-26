
class SocketsCache:

    def __init__(self):
        self.sockets = {}

    def cache_socket(self, scheme, host, port, socket):
        self.sockets[f"{scheme}://{host}:{port}"] = socket
        return True

    def get_socket(self, scheme, host, port):
        socket_name = f"{scheme}://{host}:{port}"
        if socket_name in self.sockets:
            return self.sockets[socket_name]
        else:
            return -1

    def invalidate_cache(self, scheme, host, port):
        socket_name = f"{scheme}://{host}:{port}"
        if socket_name in self.sockets:
            self.sockets[socket_name].close()
            del self.sockets[socket_name]
