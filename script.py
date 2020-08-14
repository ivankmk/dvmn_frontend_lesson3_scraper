import requests

url = 'http://tululu.org/txt.php?id=32168'

response = requests.get(url)
data = response.text

with open('max_sands.txt', 'w') as f:
    f.write(data)