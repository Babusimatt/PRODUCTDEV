import json
import os

def load_users():
    with open("users.json") as f:
        return json.load(f)

def authenticate(username, password):
    users = load_users()
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None
