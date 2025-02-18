from long_term_memory import add_message_to_db
from prompts import TEACHER_PREPROMPT
from utils import get_groq_instance, generate_messages

TEACHER_MODEL = "llama-3.3-70b-versatile"




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