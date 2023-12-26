# Base class for uri's

class URI:
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

    def make_request(self):
        raise NotImplementedError("Subclasses must implement this method")
