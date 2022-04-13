"""
Generic utility functions
"""

def string_to_dict(separated_string, separator=',') -> dict:
    """
    Takes a string e.g:
        a,b,,,,c, ,d
    and converts to:
        {'a':'', 'b':'', 'c':'', 'd':''}
    """
    output = {}
    if isinstance(separated_string, str) and len(separated_string) > 0:
        values = separated_string.split(separator)
        for value in values:
            stripped = value.strip()
            if len(stripped) > 0:
                output[stripped] = ""

    return output


def string_to_list(separated_string, separator=','):
    """
    Takes a string e.g:
        a,b, c, d
    and converts to:
        ['a', 'b', 'c', 'd']
    """
    return list(string_to_dict(separated_string, separator).keys())
