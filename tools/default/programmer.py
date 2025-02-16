import os
from groq import Groq
from prompts import PROGRAMMER_SYSTEM_PROMPT, DESCRIPTOR_SYSTEM_PROMPT

TOOLS_DIR = "tools/generated/"
PROGRAMMER_MODEL = "llama-3.3-70b-versatile"
DESCRIPTOR_MODEL = "llama-3.3-70b-versatile"


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

def generate_tool_code(program_prompt):
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

def describe_tool(code):
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

    

def save_tool(name, code):
    # Create file
    with open(TOOLS_DIR + name + ".py", "w") as f:
        f.write(code)


def programmer(program_prompt):
    code = generate_tool_code(program_prompt)
    name, description = describe_tool(code)
    save_tool(name, code)
    return name, description

programmer_client = get_groq_instance()
descriptor_client = get_groq_instance()