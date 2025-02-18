from groq import Groq
import os

def get_groq_instance():
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
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