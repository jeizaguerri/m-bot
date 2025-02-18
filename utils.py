from groq import Groq
import os

def get_groq_instance():
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    return client


def generate_messages(system_prompt, prompt):
    messages = [{
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": prompt
    }]

    return messages