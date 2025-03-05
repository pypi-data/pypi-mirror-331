import requests

url = 'http://localhost:8000/subtract'
data = {
    "args": {
        "x": 3,
        "y": 2
    }
}
while True:
    response = requests.post(url, json=data)
    print(response.json())