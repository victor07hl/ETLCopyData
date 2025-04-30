#testing the common_function's functions
from development.process_data import commun_functions
import pandas as pd
import json

def test_str_to_int():
    # Instantiate the class
    common = commun_functions()

    # Test cases
    assert common.str_to_int("123") == 123  # Valid integer string
    assert common.str_to_int("123.45") == 123  # Float string, should return integer part
    assert common.str_to_int(456) == 456  # Integer input
    assert common.str_to_int("abc") == "NoNumber"  # Non-numeric string
    assert common.str_to_int("") == "NoNumber"  # Empty string
    assert common.str_to_int(None) == "NoNumber"  # None input


