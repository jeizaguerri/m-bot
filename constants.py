# Used in the main program
BOT_NAME = "M-Bot"
MODEL = "llama-3.3-70b-versatile"
ACTION_PREFIX = "Action:"
ACTION_INPUT_PREFIX = "Action Input:"
PROGRAMMER_ACTION = "programmer"
RESPOND_TO_HUMAN_ACTION = "response_to_human"
MAX_HISTORY_LENGTH = 10
DEFAULT_TOOLS = ["response_to_human", "programmer", "calculator", "teacher"]
ERROR_MESSAGE_PREFIX = "Error:"

# Colors to use in terminal: User: Yellow, Bot: blue, tool: purple, error: red
USER_TEXT_COLOR = "\033[33m"
BOT_TEXT_COLOR = "\033[34m"
TOOL_TEXT_COLOR = "\033[35m"
ERROR_TEXT_COLOR = "\033[31m"
END_COLOR = "\033[0m"

# Tool use
DEFAULT_TOOL_DESCRIPTIONS_FILE = "tools/default_tool_descriptions.json"
GENERATED_TOOL_DESCRIPTIONS_FILE = "tools/generated_tool_descriptions.json"

# Long-term memory
INDEX_PATH = 'long_term_memory/index.faiss'
MESSAGES_DB_PATH = 'long_term_memory/messages_db.txt'

# Programmer
TOOLS_DIR = "tools/generated/"
PROGRAMMER_MODEL = "llama-3.3-70b-versatile"
DESCRIPTOR_MODEL = "llama-3.3-70b-versatile"

# Teacher
TEACHER_MODEL = "llama-3.3-70b-versatile"
