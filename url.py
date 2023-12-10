import socket
import ssl
import sockets_cache


class URL:
    def __init__(self, url, cache):
        self.parse_url(url=url)
        self.headers = {}
        self.headers["HOST"] = self.host
        self.redirect_count = 0
        # Cache the sockets to be reused by the same host
        self.cache = cache

    def parse_url(self, url):
        self.scheme, url = url.split("://", 1)
        temp = self.scheme.split(":", 1)
        self.scheme = temp[-1]
        self.view_mode = temp[0] if len(temp) > 0 else "browser"

        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "http":
            self.port = 80

        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)

        # Allow for custom ports
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        self.path = "/" + url

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
        cache_socket = self.cache.get_socket(
            scheme=self.scheme, host=self.host, port=self.port)
        s = None

        # Fix caching issues
        if cache_socket == -1:
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

            # Cache the socket to be used
            self.cache.cache_socket(
                scheme=self.scheme, host=self.host, port=self.port, socket=s)

        else:
            s = cache_socket

        headers = self.get_header_strings()
        encoding = self.get_encoding()

        s.send(
            (f"GET {self.path} HTTP/1.0\r\n{headers}\r\n\r\n".encode(encoding=encoding)))

        response = s.makefile("r", encoding=encoding, newline="\r\n")
        status_line = response.readline()

        version, status, explanation = status_line.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        # Redirect the url
        if int(status) // 100 == 3:
            self.cache.invalidate_cache(
                scheme=self.scheme, host=self.host, port=self.port)
            return self.redirect(response_headers["location"])
        else:
            # Not a redirect request
            self.redirect_count = 0
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            # Read a specific size if specified in content-length
            body = None
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

    def get_encoding(self):
        if "Content-Type" in self.headers:
            content_type = self.headers["Content-Type"]
            arr = content_type.split(";", 1)
            if len(arr) == 1:
                return "utf8"
            charset = arr[1].split("=")[1]
            return charset

        return "utf8"

    def set_entities(self, message):
        return message.replace("&lt;", "<").replace("&gt;", ">")

    def redirect(self, url):
        self.redirect_count += 1
        print(self.redirect_count)
        self.parse_redirect_url(url)
        return self.request()

    def parse_redirect_url(self, url: str):
        if url.startswith("/"):
            # The url ignores the host and scheme
            self.path = url
        else:
            self.parse_url(url)


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
    url = URL(url=sys.argv[1], cache=cache)
    url.add_header("User-Agent", "Lana")
    url.add_header("Content-Type", "text/html; charset=UTF-8")
    load(url)
