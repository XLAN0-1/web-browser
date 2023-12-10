from url import URL
test_url = URL("https://example.org/")


## Write test to ensure that replacing entities works perfectly
assert test_url.set_entites("&lt;div&gt;") == "<div>"
print("Replacing entites passed")