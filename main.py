import sys
sys.path.insert(1, "/home/xlan/web_browser/uri")
sys.path.insert(2, "/home/xlan/web_browser/cache")

import sockets_cache
import browser_cache
import http_uri

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
    body = url.make_request()

    if url.view_mode == "view-source":
        pass
        # print(url.set_entities(body))
    else:
        print(body)




if __name__ == "__main__":
    cache = sockets_cache.SocketsCache()
    url = http_uri.HttpURI(url=sys.argv[1], cache=cache)
    url.add_header("User-Agent", "Lana")
    url.add_header("Content-Type", "text/html; charset=UTF-8")
    url.add_header("Accept-Encoding", "gzip")
    load(url)
