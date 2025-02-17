from long_term_memory import add_message_to_db

def teacher(message):
    add_message_to_db(message)
    return "I have learned something new from you! Thank you!"
