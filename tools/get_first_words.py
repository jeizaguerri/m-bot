import os

def get_first_words(document: str) -> list[str]:
    """
    This function takes a document path as input, reads the document, 
    and returns the first word of every line.

    Args:
        document (str): The path to the document.

    Returns:
        list[str]: A list of the first word of every line in the document.
    """
    # Check if the file exists
    if not os.path.isfile(document):
        raise FileNotFoundError("The file does not exist.")

    # Initialize an empty list to store the first words
    first_words = []

    # Check the document format
    if document.endswith(".txt"):
        # Read the txt file
        with open(document, 'r') as file:
            for line in file:
                # Split the line into words and append the first word to the list
                words = line.split()
                if words:
                    first_words.append(words[0])

    else:
        raise ValueError("Unsupported document format.")

    return first_words