from groq import Groq
import os
import json
from dotenv import load_dotenv
from tool_use import load_tool_descriptions, save_tool_description, get_tool_descriptions, import_and_execute
from prompts import get_system_prompt, RELEVANT_INFORMATION_PREFIX, USER_MESSAGE_PREFIX
from long_term_memory import load_db, search_db
from constants import MODEL, BOT_NAME, MAX_HISTORY_LENGTH, HISTORY_FILE, ACTION_PREFIX, ACTION_INPUT_PREFIX, ERROR_MESSAGE_PREFIX, DEFAULT_TOOLS, RESPOND_TO_HUMAN_ACTION, PROGRAMMER_ACTION, TEACHER_ACTION, SESSION_CONFIG_FILE, TOOL_TEXT_COLOR, ERROR_TEXT_COLOR, USER_TEXT_COLOR, BOT_TEXT_COLOR, END_COLOR, TOOLS_DIR
from utils import get_session_directory, get_groq_instance_from_api_key
from tools.default.programmer import programmer
from tools.default.teacher import teacher

def read_env():
    load_dotenv()


def get_groq_instance(user_id, session_id):
    config_file = get_session_directory(user_id, session_id) + SESSION_CONFIG_FILE
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


def create_messages(session, message, chat_history, relevant_information):
    # Add relevant information to the chat history to the user message
    message = f"{USER_MESSAGE_PREFIX}\n" + message

    if len(relevant_information) > 0:
        message = message + f"\n{RELEVANT_INFORMATION_PREFIX}"
        for i in range(len(relevant_information)):
            message = message + f"\n{i}: {relevant_information[i]}"

    # Add system prompt
    messages = [{
        "role": "system",
        "content": get_system_prompt(get_tool_descriptions(session), BOT_NAME)
    }]

    # Add chat history
    messages = messages + chat_history

    # Add user message
    messages = messages + [
    {
        "role": "user",
        "content": message
    }]

    return messages

def parse_response(response):
    # Extract line that starts with "Action:"
    action = None
    action_input = None
    action_input_started = False
    for line in response.split("\n"):
        if line.startswith(ACTION_PREFIX):
            action = line.split(":")[1].strip()
        elif line.startswith(ACTION_INPUT_PREFIX):
            # All lines after the first line that starts with "Action Input:" are part of the action input
            action_input_started = True
            action_input = line.split(":")[1:]
            action_input = ":".join(action_input).strip()
        
        elif action_input_started:
            action_input = action_input + "\n" + line.strip()
            
    
    if action is None:
        action = "response_to_human"
        action_input = response

    # Clean action_input
    action_input = action_input.replace('"', '')

    return action, action_input

def process_user_message(session, message, chat_history):
    # Find information related to the user message in the database
    relevant_information = search_db(session, message)

    # Get response
    chat_completion = session.client.chat.completions.create(
        model = MODEL,
        messages = create_messages(session, message, chat_history, relevant_information),
        temperature=0.6,
        max_completion_tokens=1024,
        top_p=0.95,
        # reasoning_format="raw"
    )
    response = chat_completion.choices[0].message.content

    action, action_input = parse_response(response)
    print(f"{TOOL_TEXT_COLOR}Using action: {action}{END_COLOR}")

    try:
        if action in DEFAULT_TOOLS:
            tool_folder = "tools/default/"
        else:
            tool_folder = get_session_directory(session.user_id, session.session_id)+TOOLS_DIR

        if action == PROGRAMMER_ACTION:
            name, description = programmer(session, action_input)
            save_tool_description(session, name, description)
            response = f"Done! I have created the tool {name} for you. Here is a description of the tool:\n\n{description}"
        elif action == TEACHER_ACTION:
            response = teacher(session, action_input)
        else:
            response = import_and_execute(f"{tool_folder}{action}.py", action, [action_input])

        if action not in [RESPOND_TO_HUMAN_ACTION, PROGRAMMER_ACTION]:
            tool_output = f"{{\"question\": \"{message}\", \"tool\": \"{action}\", \"output\": \"{response}\"}}"
            response = process_user_message(session, tool_output, chat_history)

    except Exception as e:
        response = f"Error: {e}"

    return response
    

def load_history(session):
    history_file = get_session_directory(session.user_id, session.session_id) + HISTORY_FILE
    if not os.path.exists(history_file):
        with open(history_file, "w") as file:
            json.dump([], file)
    
    with open(history_file, "r") as file:
        chat_history = json.load(file)
    
    return chat_history


def update_history(session, user_message, bot_response):

    # Update in-memory chat history
    session.chat_history.append({"role": "user", "content": str(user_message)})
    session.chat_history.append({"role": "assistant", "content": str(bot_response)})

    # Update persistent chat history
    with open(get_session_directory(session.user_id, session.session_id) + HISTORY_FILE, "w") as file:
        json.dump(session.chat_history, file)
        
    return session.chat_history


def is_error_response(response):
    return response.startswith(ERROR_MESSAGE_PREFIX)


def chat_step(session, message):
    response = process_user_message(session, message, session.chat_history[:MAX_HISTORY_LENGTH])
    update_history(session, message, response)
    return response


def chat_loop(session):
    running = True
    while running:
        message = input(f"{USER_TEXT_COLOR}You: {END_COLOR}")
        if message == "exit":
            running = False
            break

        response = process_user_message(session, message, session.chat_history[:MAX_HISTORY_LENGTH])
        if is_error_response(response):
            print(f"{BOT_TEXT_COLOR}{BOT_NAME}: {ERROR_TEXT_COLOR}{response}{END_COLOR}")
        else:
            print(f"{BOT_TEXT_COLOR}{BOT_NAME}: {response}{END_COLOR}")

        # Save chat history
        update_history(session, message, response)


class ChatSession:
    def __init__(self, user_id, session_id, groq_api_key=None):
        # Check if the directories exist
        if not os.path.exists(get_session_directory(user_id, session_id)):
            raise FileNotFoundError(f"Session directory not found for user {user_id} and session {session_id}")

        self.user_id = user_id
        self.session_id = session_id
        if groq_api_key: self.client = get_groq_instance_from_api_key(groq_api_key)
        else: self.client = None
        self.chat_history = load_history(self)
        self.default_tool_descriptions, self.generated_tool_descriptions, self.default_tool_names, self.generated_tool_names = load_tool_descriptions(user_id, session_id)
        self.index, self.messages_db = load_db(user_id, session_id)


def create_chat_session(user_id, session_id, groq_api_key = None):
    # Check if the directories exist
    if os.path.exists(get_session_directory(user_id, session_id)):
        return ChatSession(user_id, session_id, groq_api_key)
    
    if not os.path.exists("user_data"):
        os.mkdir("user_data")
    
    if not os.path.exists(f"user_data/user_{user_id}"):
        os.mkdir(f"user_data/user_{user_id}")

    session_directory = get_session_directory(user_id, session_id)
    os.mkdir(session_directory)
    os.mkdir(session_directory + "long_term_memory")
    os.mkdir(session_directory + "tools")
    os.mkdir(session_directory + "tools/generated")
    with open(get_session_directory(user_id, session_id) + SESSION_CONFIG_FILE, "w") as file:
        if groq_api_key:
            json.dump({"GROQ_API_KEY": groq_api_key}, file)

    return ChatSession(user_id, session_id, groq_api_key)


def main():
    """
    Session variables:
    - user_id: User ID
    - session_id: Session ID
    - client: Groq client
    - chat_history: List of dictionaries with the chat history
    - tool_descriptions: List of dictionaries with the tool descriptions
    - db: List of dictionaries with the database entries
    """
    user_id = 0
    session_id = 0

    read_env()
    session = create_chat_session(user_id, session_id, os.getenv("GROQ_API_KEY"))
    chat_loop(session)

if __name__ == '__main__':
    main()