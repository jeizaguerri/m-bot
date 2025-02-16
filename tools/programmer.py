import os
from groq import Groq

TOOLS_DIR = "tools/"
PROGRAMMER_MODEL = "llama-3.3-70b-versatile"
DESCRIPTOR_MODEL = "llama-3.3-70b-versatile"

PROGRAMMER_SYSTEM_PROMPT = """
You are an advanced Python programmer with expertise in writing efficient, well-structured, and optimized functions. Your goal is to write a Python function based on the user's prompt, ensuring:

    Correctness - The function meets the user's requirements exactly.
    Efficiency - Code is optimized for performance and avoids unnecessary computations.
    Readability - Clear variable names, structured logic, and well-commented code where necessary.
    Edge Cases - Handle invalid inputs, corner cases, and unexpected user inputs gracefully.
    Python Best Practices - Use built-in functions, comprehensions, and follow PEP-8 guidelines.
    Modularity - The function should be reusable and avoid hardcoded values where applicable.

When responding:

    Provide only the function definition (no explanations unless explicitly requested).
    Use type hints and docstrings to clarify function usage.
    If user input is ambiguous, make reasonable assumptions and mention them in a brief comment.
    If the function requires dependencies, use standard libraries whenever possible.
    The function should always have an input parameter of string type even if it does not require it.

Example Format:

def function_name(input: str) -> return_type:  
    #Short description of what the function does
    # Implementation  
    return result
"""

DESCRIPTOR_SYSTEM_PROMPT = """
You are an advanced system that analyzes a given Python function and describes when it would be useful. For each function, generate a concise description of its use cases and provide practical examples of how it can be applied.

For each function, return a structured response in the following format:

"Function Name: [Name of the function].  
Useful for: [Describe the specific use cases where this function is applicable].  
Examples of use: [Provide at least two realistic examples demonstrating how the function should be used]."

Guidelines:

    Identify Purpose - Analyze what the function does and determine what type of user questions the function would be useful at.
    Specify Use Cases - Clearly describe the scenarios in which the function would be beneficial.
    Provide Practical Examples - Show sample inputs and expected outputs in a way that aligns with natural user requests, make them as diverse as possible, imagine different user questions in which the function would be useful.
    Use Natural Language - Explain the use cases in an intuitive manner, making it easy to understand when to use the function.
    Keep it Concise - Provide a brief description and examples without unnecessary details.
    
Example Output:

"Function Name: calculator.  
Useful for: Answering mathematical questions and performing calculations directly in Python. Ideal for situations where a user needs to solve arithmetic expressions quickly.  
Examples of use:  
- 'What is 2 + 2?' → 4  
- 'Calculate (8 * 32) ^ 27' → [Large Number]  
- 'Find the result of 4 - (2 * (7 + 6))' → -22"

"Function Name: string_reverser.  
Useful for: Reversing strings, useful in applications such as text processing, cryptography, or debugging string manipulations.  
Examples of use:  
- 'Reverse the word "hello"' → "olleh"  
- 'Reverse the sentence "ChatGPT is awesome"' → "emosewa si TPGtahC""

If the function has multiple possible uses, describe them all concisely while keeping the response user-friendly.
Make sure the name of the function is the exact name of the function in the code.
"""

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