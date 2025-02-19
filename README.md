# M-Bot

## Introduction

M-Bot is a versatile and powerful AI bot designed to automate various tasks and processes. M-Bot not only leverages existing tools to perform its tasks but also has the capability to create new tools as needed. This makes it highly adaptable and capable of handling a wide range of automation scenarios.

## Capabilities

- Chat and reasoning
- Tool use
- Tool creation
- Chat history
- Long term memory (faiss + facts DB)

## Getting Started

Follow these steps to set up the environment and get M-Bot running:

### 1. Create Environment from Requirements File

First, create a virtual environment and install the necessary dependencies:

#### 1.1 Using a Python Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r environments/requirements.txt
```

#### 1.2 Using a Conda Environment

```sh
conda env create -f environments/environment.yaml
conda activate mbot_env
```

### 2. Create `.env` File

Create a `.env` file in the root directory of the project and add your GROQ API key to it:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Project

With the environment set up and the `.env` file configured, you can now run the project:

```sh
python main.py
```

Please notice that packages used by the tools created by the bot are not automatically installed. You will need to manually install them in order for this tools to work.


## Useful messages
#### Listing Tools

To list all the tools that M-Bot currently has available, you can use the following command:

```
list tools
```

#### Creating a New Tool

To create a new tool, you can instruct M-Bot with a command like this:

```
create tool <tool_name> <tool_description>
```

For example:

```
create tool weather_fetcher A tool to fetch weather information from an API
```

#### Asking M-Bot to Remember Something

You can ask M-Bot to remember specific information by using the following command:

```
remember <key> <value>
```

For example:

```
remember favorite_color blue
```


Enjoy using M-Bot to automate your tasks!