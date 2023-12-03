import socket
import ssl


class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "http":
            self.port = 80

        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        self.path = "/" + url
        self.headers = {}
        self.headers["HOST"] = self.host


    def request(self):
        if self.scheme in ["http", "https"]:
            return self.http_request() 
        elif self.scheme == "file":
            return self.file_request()
        

    def file_request(self):
        with open(f".{self.path}", "r", encoding="utf8") as file:
            return file.read()

    def http_request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        # Telnet to to host
        s.connect((self.host, self.port))

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

        body = response.read()
        s.close()

        return body
    
    def add_header(self, name, value):
        self.headers[name] = value


    def get_header_strings(self):
        header_str = ""
        for key, value in self.headers.items():
            header_str += f"{key}: {value}\r\n"
        return header_str


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
    show(body)


if __name__ == "__main__":
    import sys
    url = URL(sys.argv[1])
    url.add_header("Connection", "Close")
    url.add_header("User-Agent", "Lana")
    load(url)
