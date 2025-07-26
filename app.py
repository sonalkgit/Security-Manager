from flask import Flask, request, jsonify
from pymongo import MongoClient
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

client = MongoClient("mongodb://localhost:27017/")
db = client.secret_manager
secrets_collection = db.secrets

@app.route("/home")
def health():
    return jsonify({"message": "Secret Manager API running."})

@app.route("/add-secret", methods=["POST"])
def add_secret():
    data = request.get_json()
    name = data.get("name")
    secret = data.get("secret")

    if not name or not secret:
        return jsonify({"error": "Both name and secret are required"}), 400

    encrypted_secret = cipher.encrypt(secret.encode())
    secrets_collection.update_one(
        {"name": name},
        {"$set": {"encrypted_secret": encrypted_secret.decode()}},
        upsert=True
    )

    return jsonify({"message": f"Secret for '{name}' saved successfully."}), 201

@app.route("/get-secret/<name>", methods=["GET"])
def get_secret(name):
    record = secrets_collection.find_one({"name": name})
    if not record:
        return jsonify({"error": "Secret not found"}), 404

    encrypted_secret = record["encrypted_secret"]
    decrypted_secret = cipher.decrypt(encrypted_secret.encode()).decode()

    return jsonify({"name": name, "secret": decrypted_secret}), 200

if __name__ == '__main__':
    print("ENCRYPTION KEY (store this securely!):", ENCRYPTION_KEY.decode())
    app.run(debug=True, port=5000)
