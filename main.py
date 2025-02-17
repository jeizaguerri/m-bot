from groq import Groq
import os
from dotenv import load_dotenv
from tool_use import load_tool_descriptions, save_tool_description, get_tool_descriptions, import_and_execute
from prompts import get_system_prompt, RELEVANT_INFORMATION_PREFIX, USER_MESSAGE_PREFIX
from long_term_memory import load_db, search_db

BOT_NAME = "M-Bot"
MODEL = "llama-3.3-70b-versatile"
ACTION_PREFIX = "Action:"
ACTION_INPUT_PREFIX = "Action Input:"
PROGRAMMER_ACTION = "programmer"
RESPOND_TO_HUMAN_ACTION = "response_to_human"
MAX_HISTORY_LENGTH = 10
DEFAULT_TOOLS = ["response_to_human", "programmer", "calculator", "teacher"]

# Colorst to use in terminal: User: Yellow, Bot: blue, tool: purple
USER_TEXT_COLOR = "\033[33m"
BOT_TEXT_COLOR = "\033[34m"
TOOL_TEXT_COLOR = "\033[35m"
END_COLOR = "\033[0m"

def read_env():
    load_dotenv()


def get_groq_instance():
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    return client


def create_messages(message, chat_history, relevant_information):
    # Add relevant information to the chat history to the user message
    message = f"{USER_MESSAGE_PREFIX}\n" + message

    if len(relevant_information) > 0:
        message = message + f"\n{RELEVANT_INFORMATION_PREFIX}"
        for i in range(len(relevant_information)):
            message = message + f"\n{i}: {relevant_information[i]}"

    # Add system prompt
    messages = [{
        "role": "system",
        "content": get_system_prompt(get_tool_descriptions(), BOT_NAME)
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
            action_input = line.split(":")[1].strip()
        
        elif action_input_started:
            action_input = action_input + "\n" + line.strip()
            
    
    if action is None:
        action = "response_to_human"
        action_input = response

    # Clean action_input
    action_input = action_input.replace('"', '')

    return action, action_input

def process_user_message(client, message, chat_history):
    # Find information related to the user message in the database
    relevant_information = search_db(message)

    # Get response
    chat_completion = client.chat.completions.create(
        model = MODEL,
        messages = create_messages(message, chat_history, relevant_information),
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
            tool_folder = "tools/default"
        else:
            tool_folder = "tools/generated"

        response = import_and_execute(f"{tool_folder}/{action}.py", action, [action_input])
        if action == PROGRAMMER_ACTION:
            name, description = response
            # Add the tool to the list of tools
            save_tool_description(name, description)

            response = f"Done! I have created the tool {name} for you. Here is a description of the tool:\n\n{description}"
        
        if action not in [RESPOND_TO_HUMAN_ACTION, PROGRAMMER_ACTION]:
            tool_output = f"{{\"question\": \"{message}\", \"tool\": \"{action}\", \"output\": \"{response}\"}}"
            response = process_user_message(client, tool_output, chat_history)

    except Exception as e:
        response = f"Error: {e}"

    return response
    
def update_history(chat_history, user_message, bot_response):
    chat_history.append({"role": "user", "content": str(user_message)})
    chat_history.append({"role": "assistant", "content": str(bot_response)})

    if len(chat_history) > MAX_HISTORY_LENGTH:
        chat_history = chat_history[-MAX_HISTORY_LENGTH:]
        
    return chat_history


def end_chat():
    print("Goodbye!")
    

def chat_loop(client):
    running = True
    chat_history = []
    while running:
        message = input(f"{USER_TEXT_COLOR}You: {END_COLOR}")
        if message == "exit":
            running = False
            break
        response = process_user_message(client, message, chat_history)
        print(f"{BOT_TEXT_COLOR}{BOT_NAME}: {response}{END_COLOR}")

        # Save chat history
        chat_history = update_history(chat_history, message, response)
    
    end_chat()


def main():
    read_env()
    load_db()
    load_tool_descriptions()
    client = get_groq_instance()
    chat_loop(client)

if __name__ == '__main__':
    main()