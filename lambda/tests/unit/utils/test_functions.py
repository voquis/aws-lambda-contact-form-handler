"""
Utils unit tests
"""

from app_handler.utils.functions import string_to_dict
from app_handler.utils.functions import string_to_list

def test_string_to_dict():
    """
    Test string to dictionary with separator
    """
    assert not string_to_dict(None)
    assert not string_to_dict({})
    assert not string_to_dict('')
    assert string_to_dict('a,b,,') == {'a':'', 'b':''}
    assert string_to_dict('d|s|d', '|') == {'d':'','s':''}

def test_string_to_list():
    """
    Test string to list with separator
    """
    assert not string_to_list(None)
    assert not string_to_list({})
    assert not string_to_list('')
    assert string_to_list('a,,,b') == ['a','b']
    assert string_to_list('d|s||d', '|') == ['d','s']
