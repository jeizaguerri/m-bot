def calculator(expression):
    expression = expression.replace("^", "**")
    expression = expression.replace("x", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("mod", "%")
    return eval(expression)
    