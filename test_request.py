import requests

url = "http://127.0.0.1:5000/chat"
data = {
    "message": "Hey Bacchu, kya bolti tu?"
}

response = requests.post(url, json=data)

print("Bacchu says:", response.json()["reply"])
