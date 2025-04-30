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

def test_strjson2pd_df():
    # Instantiate the class
    common = commun_functions()

    # Test cases
    valid_json = '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'
    df = common.strjson2pd_df(valid_json)
    assert isinstance(df, pd.DataFrame)  # Should return a DataFrame
    assert len(df) == 2  # Should have 2 rows
    assert list(df.columns) == ["id", "name"]  # Should have the correct columns

    empty_json = '[]'
    df = common.strjson2pd_df(empty_json)
    assert df is None  # Should return None for empty JSON

    invalid_json = '{"id": 1, "name": "Alice"}'  # Not a list of objects
    try:
        common.strjson2pd_df(invalid_json)
        assert False  # Should raise an exception
    except json.JSONDecodeError:
        pass  # Expected behavior

    bytes_json = b'[{"id": 1, "name": "Alice"}]'
    df = common.strjson2pd_df(bytes_json)
    assert isinstance(df, pd.DataFrame)  # Should handle bytes input
    assert len(df) == 1  # Should have 1 row
    assert list(df.columns) == ["id", "name"]  # Should have the correct columns

    invalid_input = None
    try:
        common.strjson2pd_df(invalid_input)
        assert False  # Should raise an exception
    except TypeError:
        pass  # Expected behavior

