"""
Example unit tests
"""

from example import __version__
from example import example


def test_version():
    """
    Test package version
    """
    assert __version__ == '0.1.0'


def test_example_function():
    """
    Test example function
    """
    assert example.example_function('a') == 'a'
