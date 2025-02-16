import wikipedia
from transformers import T5ForConditionalGeneration, T5Tokenizer
from googlesearch import search
from bs4 import BeautifulSoup
import requests

def online_question_answerer(question: str) -> str:
    """
    This function takes a user's question as input, searches online for relevant information, 
    and returns a concise answer to the user's question.

    Parameters:
    question (str): The user's question.

    Returns:
    str: A concise answer to the user's question.
    """

    # First, try to find an answer on Wikipedia
    try:
        # Search for the question on Wikipedia
        search_results = wikipedia.search(question, results=1)
        
        # If search results are found, get the summary of the first result
        if search_results:
            page = wikipedia.page(search_results[0], auto_suggest=False)
            return page.summary[:200] + "..."

    # If no results are found or an error occurs, try searching the web
    except Exception as e:
        print(f"Wikipedia search failed: {e}")
        
    # Initialize the T5 model and tokenizer
    model = T5ForConditionalGeneration.from_pretrained('t5-small')
    tokenizer = T5Tokenizer.from_pretrained('t5-small')

    # Search the web for the question
    url_list = []
    for url in search(question, num_results=5):
        url_list.append(url)

    # Initialize an empty string to store the answer
    answer = ""

    # Loop through each URL
    for url in url_list:
        try:
            # Send a GET request to the URL
            response = requests.get(url)

            # If the request is successful, parse the HTML
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove all script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get the text from the HTML
                text = soup.get_text()

                # Tokenize the input question
                input_ids = tokenizer.encode("answer the question: " + question, return_tensors="pt")

                # Generate the answer
                output = model.generate(input_ids, max_length=50)

                # Decode the answer
                answer = tokenizer.decode(output[0], skip_special_tokens=True)

                # Add the text to the answer
                answer += text[:200] + "..."

                # If the answer is not empty, break the loop
                if answer:
                    break

        except Exception as e:
            print(f"Failed to search {url}: {e}")

    # If the answer is still empty, return a default message
    if not answer:
        answer = "Sorry, I couldn't find an answer to your question."

    return answer