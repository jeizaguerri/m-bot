from groq import Groq
import os
from long_term_memory import add_message_to_db
from prompts import TEACHER_PREPROMPT

TEACHER_MODEL = "llama-3.3-70b-versatile"

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


def generate_fact(message):
    # Prepare messages
    messages = generate_messages(TEACHER_PREPROMPT, message)

    # Generate code
    fact_completion = fact_creator_client.chat.completions.create(
        model = TEACHER_MODEL,
        messages = messages
    )

    fact = fact_completion.choices[0].message.content

    return fact


def teacher(message):
    # Convert message to fact
    fact = generate_fact(message)

    # Add fact to database
    add_message_to_db(fact)

    return "Information added to memory:" + fact

fact_creator_client = get_groq_instance()