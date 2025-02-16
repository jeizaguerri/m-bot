from datetime import datetime

def get_current_time(input: str) -> str:
    # Returns the current time in the format HH
    current_time = datetime.now().strftime("%H")
    return current_time