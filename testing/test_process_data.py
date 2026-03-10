import json
import pytest
import pandas as pd
from development.process_data import commun_functions, process_data


class TestStrToInt:
    def setup_method(self):
        self.common = commun_functions()

    def test_valid_integer_string(self):
        assert self.common.str_to_int("123") == 123

    def test_float_string_returns_integer_part(self):
        assert self.common.str_to_int("123.45") == 123

    def test_integer_input(self):
        assert self.common.str_to_int(456) == 456

    def test_non_numeric_string_returns_none(self):
        assert self.common.str_to_int("abc") is None

    def test_empty_string_returns_none(self):
        assert self.common.str_to_int("") is None

    def test_none_input_returns_none(self):
        assert self.common.str_to_int(None) is None

    def test_zero(self):
        assert self.common.str_to_int("0") == 0

    def test_negative_string_returns_none(self):
        assert self.common.str_to_int("-5") is None


class TestStrJson2PdDf:
    def setup_method(self):
        self.common = commun_functions()

    def test_valid_json_bytes(self):
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        raw = json.dumps(data).encode('utf-8')
        df = self.common.strjson2pd_df(raw)
        assert df is not None
        assert len(df) == 2
        assert list(df.columns) == ["id", "name"]

    def test_valid_json_string(self):
        data = [{"id": 1, "job": "Engineer"}]
        raw = json.dumps(data)
        df = self.common.strjson2pd_df(raw)
        assert df is not None
        assert len(df) == 1

    def test_empty_list_returns_none(self):
        raw = json.dumps([]).encode('utf-8')
        result = self.common.strjson2pd_df(raw)
        assert result is None


class TestProcessData:
    def setup_method(self):
        self.proc = process_data()

    def test_process_departments_drops_nulls(self):
        df = pd.DataFrame({'id': [1, None, 3], 'department': ['HR', None, 'IT']})
        schema = {'id': int, 'department': str}
        result, nulls = self.proc.process_departments(df, schema)
        assert len(result) == 2
        assert len(nulls) == 1

    def test_process_jobs_drops_nulls(self):
        df = pd.DataFrame({'id': [1, 2], 'job': ['Engineer', None]})
        schema = {'id': int, 'job': str}
        result, nulls = self.proc.process_jobs(df, schema)
        assert len(result) == 1
        assert len(nulls) == 1

    def test_process_hired_filters_invalid_ids(self):
        df = pd.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'DATETIME': ['2021-01-01', '2021-02-01'],
            'department_id': ['10', 'abc'],
            'job_id': ['5', '6'],
        })
        schema = {'id': int, 'name': str, 'DATETIME': str, 'department_id': int, 'job_id': int}
        result, nulls = self.proc.process_hired(df, schema)
        assert len(result) == 1
        assert result.iloc[0]['name'] == 'Alice'

    def test_get_process_returns_correct_function(self):
        assert self.proc.get_process('departments') == self.proc.process_departments
        assert self.proc.get_process('jobs') == self.proc.process_jobs
        assert self.proc.get_process('hired_employees') == self.proc.process_hired

    def test_get_process_raises_on_unknown_table(self):
        with pytest.raises(KeyError):
            self.proc.get_process('unknown_table')
