import requests

url = "https://www.rekrute.com/offre.html"

response = requests.get(url)

html = response.text

with open("page.html", "w", encoding="utf-8") as f:
    f.write(html)
    