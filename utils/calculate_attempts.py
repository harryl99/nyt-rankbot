from utils.patterns import mini_pattern, wordle_pattern


def connections_attempts(message):
    """
    Count the number of attempts to complete Connections.

    Parameters:
    - message (str): The input message containing Connections game information.

    Returns:
    - int: The number of connection attempts.
    """
    connection_colours = "🟨🟩🟦🟪"
    connections_lines = message.splitlines()
    connections_lines = [
        line
        for line in connections_lines
        if any(square in line for square in connection_colours)
    ]
    attempts = len(connections_lines)
    return attempts


def mini_time(message):
    """
    Extract the amount of time to complete the Mini.

    Parameters:
    - message (str): The input message containing Mini game information.

    Returns:
    - str: The extracted time.
    """
    time = mini_pattern.search(message).group(1)
    return time


def wordle_attempts(message):
    """
    Count the number of attempts to complete Wordle.

    Parameters:
    - message (str): The input message containing Wordle game information.

    Returns:
    - str: The extracted number of attempts.
    """
    attempts = wordle_pattern.search(message).group(1)
    attempts = attempts.replace("X", "7")
    return attempts
