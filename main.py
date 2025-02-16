from groq import Groq
import os
from dotenv import load_dotenv
from tool_use import load_tool_descriptions, save_tool_description, get_tool_descriptions, import_and_execute
from prompts import get_system_prompt

BOT_NAME = "M-Bot"
MODEL = "llama3-70b-8192"
ACTION_PREFIX = "Action:"
ACTION_INPUT_PREFIX = "Action Input:"
PROGRAMMER_ACTION = "programmer"
RESPOND_TO_HUMAN_ACTION = "response_to_human"
MAX_HISTORY_LENGTH = 10
DEFAULT_TOOLS = ["response_to_human", "programmer", "calculator"]


def read_env():
    load_dotenv()


def get_groq_instance():
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    return client


def create_messages(message, chat_history):
    messages = [{
        "role": "system",
        "content": get_system_prompt(get_tool_descriptions(), BOT_NAME)
    }]
    messages = messages + chat_history
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
    for line in response.split("\n"):
        if line.startswith(ACTION_PREFIX):
            action = line.split(":")[1].strip()
        elif line.startswith(ACTION_INPUT_PREFIX):
            action_input = line.split(":")[1].strip()
    
    if action is None:
        action = "response_to_human"
        action_input = response

    # Clean action_input
    action_input = action_input.replace('"', '')

    return action, action_input

def process_user_message(client, message, chat_history):
    chat_completion = client.chat.completions.create(
        model = MODEL,
        messages = create_messages(message, chat_history),
        temperature=0.6,
        max_completion_tokens=1024,
        top_p=0.95,
        # reasoning_format="raw"
    )
    response = chat_completion.choices[0].message.content

    action, action_input = parse_response(response)
    print(f"Using action: {action}")

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
            print(f"Tool output: {tool_output}")
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


def chat_loop(client):
    running = True
    chat_history = []
    while running:
        message = input("You: ")
        if message == "exit":
            running = False
            break
        response = process_user_message(client, message, chat_history)
        print(f"{BOT_NAME}: {response}")

        # Save chat history
        chat_history = update_history(chat_history, message, response)
    
    print("Goodbye!")


def main():
    read_env()
    load_tool_descriptions()
    client = get_groq_instance()
    chat_loop(client)

if __name__ == '__main__':
    main()