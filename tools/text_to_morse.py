def text_to_morse(input_str: str) -> str:
    """
    Convert normal text strings to Morse code.

    The function uses a dictionary to map English characters to Morse code.
    It handles both uppercase and lowercase letters, as well as spaces and punctuation.

    Args:
        input_str (str): The input text string to be converted.

    Returns:
        str: The Morse code equivalent of the input string.
    """
    morse_code_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
        'Y': '-.--', 'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        ' ': '/', ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', 
        '-': '-....-', '(': '-.--.', ')': '-.--.-'
    }

    # Convert input string to uppercase for consistency
    input_str = input_str.upper()
    
    # Use list comprehension to map characters to Morse code
    morse_code = [morse_code_dict.get(char, '') for char in input_str]
    
    # Join the Morse code characters into a single string
    morse_code_str = ' '.join(morse_code)
    
    return morse_code_str

# Example usage:
print(text_to_morse('Hello World'))