def decimal_to_binary(input: str) -> str:  
    # Convert decimal to binary, assuming input is a string representation of an integer
    decimal_number = int(input)
    return bin(decimal_number)[2:]

# Example usage:
print(decimal_to_binary("10"))  # Output: 1010