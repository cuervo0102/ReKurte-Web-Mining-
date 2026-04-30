import requests
r = requests.get("https://httpbin.org/user-agent")
print(r.json())