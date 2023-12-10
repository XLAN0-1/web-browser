import socket
import ssl
import sockets_cache

class URL:
    def __init__(self, url, cache):
        self.scheme, url = url.split("://", 1)

        temp = self.scheme.split(":", 1)
        self.scheme = temp[-1]
        self.view_mode = temp[0] if len(temp) > 0 else "browser"


        assert self.scheme in ["http", "https", "file", "view-source:https"]

        if self.scheme == "http":
            self.port = 80

        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)

        ## Allow for custom ports
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        self.path = "/" + url
        self.headers = {}
        self.headers["HOST"] = self.host

        # Cache the sockets to be reused by the same host
        self.cache = cache


    def request(self):
        if self.scheme in ["http", "https"]:
            return self.http_request() 
        elif self.scheme == "file":
            return self.file_request()

        
    def file_request(self):
        with open(f".{self.path}", "r", encoding="utf8") as file:
            return file.read()
        
    def view_source_request(self):
        return self.set_entities(self.request())

    def http_request(self):
        cache_socket = self.cache.get_socket(scheme=self.scheme, host=self.host, port=self.port)
        s = None

        if cache_socket == -1:
            s= socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )

            # Telnet to to host
            s.connect((self.host, self.port))

            # Cache the socket to be used
            self.cache.cache_socket(scheme=self.scheme, host=self.host, port=self.port, socket=s)

        else:
            s = cache_socket



        if self.port == 443:
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = self.get_header_strings()
        s.send(
            (f"GET {self.path} HTTP/1.0\r\n{headers}\r\n\r\n".encode("utf8")))


        response = s.makefile("r", encoding="utf8", newline="\r\n")
        status_line = response.readline()
        version, status, explanation = status_line.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Read a specific size if specified in content-length
        body = None
        print("here")
        if "Content-Length" in self.headers:
            body = response.read(self.headers["Content-Length"])
        else:
            # Read the whole content
            body = response.read()

        return body

    def add_header(self, name, value):
        self.headers[name] = value


    def get_header_strings(self):
        header_str = ""
        for key, value in self.headers.items():
            if key == "Content-Length":
                continue
            header_str += f"{key}: {value}\r\n"
        return header_str
    
    def set_entities(self, message):
        return message.replace("&lt;", "<").replace("&gt;", ">")
    


def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


def load(url):
    body = url.request()

    if url.view_mode == "view-source":
        print(url.set_entities(body))
    else:
        print(body)


if __name__ == "__main__":
    import sys
    cache = sockets_cache.SocketsCache()
    url = URL(sys.argv[1], cache=cache)
    url.add_header("Connection", "Close")
    url.add_header("User-Agent", "Lana")
    url.add_header("Content-Length", 512)
    load(url)
