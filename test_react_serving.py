from starlette.testclient import TestClient
from web_app import app

client = TestClient(app)
resp = client.get("/")
print("GET / Status Code:", resp.status_code)
print("Preview:\n", resp.text)
assert "<div id=\"root\"></div>" in resp.text
print("\n[SUCCESS] React Application is being served on /!")
