import requests

res = requests.post("http://127.0.0.1:5000/chat", json={"message": "Bacchu, kya kar raha hai tu?"})
print("👉 Bacchu says:", res.json())
