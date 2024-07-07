import os
import socket
import ssl
import gzip
from .uri import URI

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

class HttpURI(URI):
    def view_source_request(self):
        return self.set_entities(self.request())

    def get_socket(self):
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

        return s

    def make_request(self):
        s = self.get_socket()
        headers = self.get_header_strings()
        encoding = self.get_encoding()

        s.send(
            (f"GET {self.path} HTTP/1.0\r\n{headers}\r\n\r\n".encode(encoding=encoding)))

        response = s.makefile("rb", encoding=encoding, newline="\r\n")

        status_line = response.readline().decode(encoding=encoding)

        version, status, explanation = status_line.split(" ", 2)

        response_headers = self.get_response_headers(response=response)


        # Redirect the url
        if int(status) // 100 == 3:
            self.cache.invalidate_cache(
                scheme=self.scheme, host=self.host, port=self.port)
            return self.redirect(response_headers["location"])
        else:
            # Not a redirect request
            self.redirect_count = 0

            # Read a specific size if specified in content-length
            body = None
            if "Content-Length" in self.headers:
                body = response.read(self.headers["Content-Length"])
            else:
                body = response.read()
                if "content-encoding" in response_headers: 
                   body = self.decompress_body(body)

            # Cache the response 
            return body.decode(encoding=encoding)
        
    def decompress_body(self, body):

        body = gzip.decompress(body)
        return body 

    def add_header(self, name, value):
        self.headers[name] = value

    def cache_response(self):
        pass

    def get_response_headers(self, response):
        response_headers = {}

        while True:
            line = response.readline().decode(encoding=self.get_encoding())

            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        return response_headers

    def get_header_strings(self):
        header_str = ""
        for key, value in self.headers.items():
            if key == "Content-Length":
                continue
            header_str += f"{key}: {value}\r\n"

        print('HEADERS: ', header_str)
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

    def set_entities(self, body):
        return body.replace("&lt;", "<").replace("&gt;", ">")
    
    def decode(self, body):
        if type(body) == "bytes":
            return body.decode(encoding="utf8")
        
        return body

    def redirect(self, url):
        self.redirect_count += 1
        print(self.redirect_count)
        self.parse_redirect_url(url)
        return self.make_request()

    def parse_redirect_url(self, url: str):
        if url.startswith("/"):
            # The url ignores the host and scheme
            self.path = url
        else:
            self.parse_url(url)

    def lex(self, body):
        body = self.set_entities(body)
        out = []
        buffer = ""    
        in_tag = False


        for c in body:
            if c == "<":
                in_tag = True
                if buffer: out.append(Text(buffer))
                buffer = ""
            elif c == ">":
                in_tag = False
                out.append(Tag(buffer))
                buffer = ""
            else:
                buffer += c

        if not in_tag and buffer:
            out.append(Text(buffer))

        return out

