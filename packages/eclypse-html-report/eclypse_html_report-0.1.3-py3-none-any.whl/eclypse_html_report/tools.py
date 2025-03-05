"""Auxiliary functions for the HTML report generation."""

from typing import Any


def format_float(value: float) -> str:
    """Format a float to a string with 4 decimal places, if necessary.

    .. code-block:: python

            value = 10.123456
            print(format_float(value))  # 10.1235

            value = 10.0
            print(format_float(value))  # 10

    Args:
        value (float): The float to format.

    Returns:
        str: The formatted string.
    """
    return f"{value:.4f}" if value != int(value) else str(int(value))


def to_float(value: Any):
    """Convert a value to a float if possible.

    Args:
        value: The value to convert.

    Returns:
        float: The float value, or the original value if it cannot be converted.
    """
    try:
        return float(value)
    except ValueError:
        return value


def snake_to_title(s: str) -> str:
    """Convert a snake_case string to a title case string.

    .. code-block:: python

            s = "my_snake_case_sentence"
            print(snake_to_title(s))  # My Snake Case Sentence

    Args:
        s (str): The snake_case string to convert.

    Returns:
        str: The title case string.
    """
    return s.replace("_", " ").title()
