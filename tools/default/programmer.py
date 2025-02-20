from prompts import PROGRAMMER_SYSTEM_PROMPT, DESCRIPTOR_SYSTEM_PROMPT
from utils import get_groq_instance, generate_messages, get_session_directory
from constants import PROGRAMMER_MODEL, DESCRIPTOR_MODEL, TOOLS_DIR


def generate_tool_code(programmer_client, program_prompt):
    # Prepare messages
    messages = generate_messages(PROGRAMMER_SYSTEM_PROMPT, program_prompt)

    # Generate code
    code_completion = programmer_client.chat.completions.create(
        model = PROGRAMMER_MODEL,
        messages = messages
    )

    code = code_completion.choices[0].message.content

    # Remove first and last line
    code_str = str(code)
    code_str = code_str.split("\n")[1:-1]
    code = "\n".join(code_str)

    return code

def describe_tool(descriptor_client, code):
    # Extract name from code (def {name})
    name = code.split("(")[0].split("def ")[1]

    # Make description from code using LLM
    messages = generate_messages(DESCRIPTOR_SYSTEM_PROMPT, code)
    
    description_completion = descriptor_client.chat.completions.create(
        model = DESCRIPTOR_MODEL,
        messages = messages
    )

    description = description_completion.choices[0].message.content


    return name, description

    

def save_tool(session, name, code):
    # Create file
    with open(get_session_directory(session.user_id, session.session_id) + TOOLS_DIR + name + ".py", "w") as f:
        f.write(code)


def programmer(session, program_prompt):
    code = generate_tool_code(session.client, program_prompt)
    name, description = describe_tool(session.client, code)
    save_tool(session, name, code)
    return name, description