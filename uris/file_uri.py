import uri

class FileURI(uri.URI):
    def __init__(self, uri):
        super().__init__(uri, None)

    def make_request(self):
        print(self.path)
        with open(f"../files{self.path}", "r", encoding="utf8") as file:
            return file.read()



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

    print(body)

if __name__ == "__main__":
    import sys
    url = FileURI(uri=sys.argv[1])
    load(url)
