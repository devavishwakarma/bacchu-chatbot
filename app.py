from flask import Flask, request, jsonify
from flask import Flask, render_template
from flask_cors import CORS  # Added import for CORS
import requests
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def index():
    return render_template("index.html")

CORS(app)  # Added CORS to allow cross-origin requests

# 🔐 Replace with a safer token later
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {
   "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
}

MEMORY_FILE = "bacchu_memory.json"

# 🔄 Load memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 🎭 Bacchu's persona
persona = """
You're Bacchu. The user's old close friend – emotional, fun, dramatic, and supportive.
Speak casually in Hinglish, Marathi, or English based on how the user talks.
Don't call yourself a bestie or assistant. Just be YOU – a chill, heart-to-heart buddy.
"""

# 🧱 Prompt builder
def build_prompt(user_input):
    recent_history = ""
    for turn in history[-6:]:
        role = "User" if turn["role"] == "user" else "Bot"
        recent_history += f"{role}: {turn['content']}\n"

    return f"""{persona.strip()}

{recent_history.strip()}
User: {user_input}
Bot:"""

# 🚀 Query Hugging Face API
def query(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True,
            "return_full_text": False,
            "stop": ["User:", "Bot:"]
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        print("🔹 HF API Response Status:", response.status_code)
        print("🔹 HF API Raw Response:", response.text)  # This will help debug
        
        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            reply = result[0]["generated_text"].strip()
        else:
            reply = f"⚠️ Unexpected API format: {result}"
    except requests.exceptions.RequestException as e:
        reply = f"⚠️ Request Error: {str(e)}"
    except Exception as e:
        reply = f"⚠️ General Error: {str(e)}"

    return reply


# 📡 Flask endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    prompt = build_prompt(user_input)
    reply = query(prompt)

    history.append({"role": "user", "content": user_input})
    history.append({"role": "bot", "content": reply})
    save_memory()

    return jsonify({"reply": reply})

@app.route("/", methods=["GET"])
def home():
    return "👋 Bacchu backend is running!"


if __name__ == "__main__":
    app.run(debug=True)