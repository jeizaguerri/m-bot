import streamlit as st
from main import *
from streamlit.components.v1 import html
from constants import SESSION_COUNTER_FILE
import torch

st.set_page_config(layout="wide")
torch.classes.__path__ = []

# Function to read the counter from a file
def read_counter():
    if os.path.exists(SESSION_COUNTER_FILE):
        with open(SESSION_COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    return 0

# Function to update the counter
def write_counter(value):
    with open(SESSION_COUNTER_FILE, "w") as f:
        f.write(str(value))

# Initialize counter on first load
if "counter" not in st.session_state:
    st.session_state.counter = read_counter() + 1  # Increment on new page load
    write_counter(st.session_state.counter)  # Save updated count


user_id = 0
session_id = st.session_state.counter
session = create_chat_session(user_id, session_id, os.getenv("GROQ_API_KEY"))
descriptions = session.default_tool_descriptions + session.generated_tool_descriptions
tool_names = session.default_tool_names + session.generated_tool_names





# Api key on the bottom
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
if not groq_api_key:
        st.sidebar.warning("Please enter your Groq API key!", icon="⚠")
# Add a button to the sidebar (Header first):
st.sidebar.header(':blue[Tools]')
tool_filter = st.sidebar.text_input("Filter tools")
filtered_tool_indexes = [i for i, tool_name in enumerate(tool_names) if tool_filter.lower() in tool_name.lower()]
filtered_tools = [tool_names[i] for i in filtered_tool_indexes]
filtered_desc = [descriptions[i] for i in filtered_tool_indexes]
tool_selected = st.sidebar.pills(
    "Available tools",
    options=range(len(filtered_tools)),
    format_func=lambda i: tool_names[i],
    selection_mode="single",
)

st.sidebar.header(':blue[Stored Data]')
show_stored_data = st.sidebar.button("Check stored data")


st.title("Hey, this is :blue[M-BOT]")
left_column, right_column = st.columns([0.7, 0.3], border=True)

# Right info column
with right_column.container(height=400, border=False):
    if show_stored_data:
        data = session.messages_db
        
        st.header(":blue[Data stored in long-term memory]")
        st.table(data)
    elif tool_selected is not None:
            st.header(f":blue[{filtered_tools[tool_selected]}]")
            st.write(filtered_desc[tool_selected])
    else:
        st.write("Select a tool to view its description")

# Left chat column
# Show the chat history
with left_column.container(height=400, border=False):
    for message in session.chat_history:
        with st.chat_message("assistant", avatar = "1x1.png"):
            if message["role"] == "user":
                # Aligned right
                st.markdown(f"<div style='display: flex; justify-content: flex-end;'><div style=\"background-color: #212121; padding: 8px; border-radius: 10px 10px 0px 10px; display: inline-block;\">{message['content']}</div></div>", unsafe_allow_html=True)
            else:
                st.text(message["content"])

loading_text = left_column.empty()

if text := left_column.chat_input("Ask anything..."):
    if groq_api_key:
        session = create_chat_session(user_id, session_id, groq_api_key)
        try:
            loading_text.status("M-BOT is typing...")
            response = chat_step(session, text)
            st.rerun()
        except Exception as e:
            loading_text.error("Invalid Groq API key")
    else:
         loading_text.error("Please enter your Groq API key")

