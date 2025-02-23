from groq import Groq
import os
import json

def get_groq_instance(user_id, session_id):
    config_file = get_session_directory(user_id, session_id) + "config.json"
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found at {config_file}")
    
    with open(config_file, "r") as file:
        config = json.load(file)
        if "GROQ_API_KEY" not in config:
            raise KeyError("api_key not found in config file")
        api_key = config["GROQ_API_KEY"]

    client = Groq(
        api_key=api_key,
    )
    return client


def get_groq_instance_from_api_key(groq_api_key):
    client = Groq(
        api_key=groq_api_key,
    )

    return client


def generate_messages(system_prompt, prompt, chat_history = None):
    messages = [{
        "role": "system",
        "content": system_prompt
    }]

    if chat_history and len(chat_history) > 0:
        messages = messages + chat_history

    messages = messages + [{
        "role": "user",
        "content": prompt
    }]

    return messages


def get_session_directory(user_id, session_id):
    return f"user_data/user_{user_id}/session_{user_id}_{session_id}/"