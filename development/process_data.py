import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class commun_functions:
    def str_to_int(self, str_number: str) -> int | None:
        str_number = str(str_number)
        str_number = str_number.split('.')[0]
        if str_number.isnumeric():
            return int(str_number)
        return None

    def strjson2pd_df(self, str_json) -> pd.DataFrame | None:
        if isinstance(str_json, bytes):
            bstr_json = str_json
        else:
            bstr_json = bytes(str_json, 'utf-8')
        json_object = json.loads(bstr_json)
        df = pd.DataFrame(json_object)
        return df if len(df) > 0 else None


class process_data(commun_functions):

    def _process_generic(self, df: pd.DataFrame, schema: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_nulls = df[df.isna().any(axis=1)]
        df = df.dropna().copy()
        for col, dtype in schema.items():
            df[col] = df[col].astype(dtype)
        return df, df_nulls

    def process_hired(self, df: pd.DataFrame, schema: dict = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_nulls = df[df.isna().any(axis=1)]
        df = df.dropna().copy()

        df['department_id'] = df['department_id'].apply(self.str_to_int)
        df['job_id'] = df['job_id'].apply(self.str_to_int)
        df = df[df['department_id'].notna() & df['job_id'].notna()]

        for col, dtype in schema.items():
            df[col] = df[col].astype(dtype)

        return df, df_nulls

    def process_departments(self, df: pd.DataFrame, schema: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
        return self._process_generic(df, schema)

    def process_jobs(self, df: pd.DataFrame, schema: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
        return self._process_generic(df, schema)

    def get_process(self, table: str):
        process_function = {
            'departments': self.process_departments,
            'hired_employees': self.process_hired,
            'jobs': self.process_jobs,
        }
        if table not in process_function:
            raise KeyError(f"No processing function defined for table '{table}'")
        return process_function[table]
