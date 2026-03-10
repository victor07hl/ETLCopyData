import os
import logging
import pandas as pd
from datetime import datetime
from process_data import process_data
from connections import connections
from queries import queries

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'xlsx', 'csv'}

TABLE_SCHEMAS = {
    'departments': {'id': int, 'department': str},
    'hired_employees': {'id': int, 'name': str, 'DATETIME': str, 'department_id': int, 'job_id': int},
    'jobs': {'id': int, 'job': str},
}


class migratedata(process_data, connections):

    def get_metadata(self, source_name: str) -> dict:
        if source_name not in TABLE_SCHEMAS:
            raise KeyError(f"No schema defined for source '{source_name}'")
        return TABLE_SCHEMAS[source_name]

    def read_data_source(self, source: str) -> tuple[pd.DataFrame, str]:
        filename = os.path.basename(source)
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip('.')

        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension '.{ext}'. Supported: {SUPPORTED_EXTENSIONS}")

        if ext == 'xlsx':
            df = pd.read_excel(source, header=None)
        else:
            df = pd.read_csv(source, header=None)

        df.columns = list(self.get_metadata(name).keys())
        return df, name

    def _save_nulls(self, df_nulls: pd.DataFrame, nulls_path: str) -> None:
        if len(df_nulls) == 0:
            return
        os.makedirs(os.path.dirname(nulls_path), exist_ok=True)
        mode = 'a' if os.path.exists(nulls_path) else 'w'
        df_nulls.to_csv(nulls_path, index=False, mode=mode, header=(mode == 'w'))
        logger.info("Nulls saved to %s", nulls_path)

    def batch_migration(self, file: str, sink_schema: str, sink_nulls: str) -> None:
        df, name = self.read_data_source(file)
        df, df_nulls = self.get_process(name)(df, self.get_metadata(name))

        nulls_path = os.path.join(sink_nulls, 'batch', f'{name}_nulls.csv')
        self._save_nulls(df_nulls, nulls_path)

        engine = self.engine()
        df.to_sql(name=name, con=engine, schema=sink_schema, if_exists='replace', index=False)
        logger.info("Table %s loaded successfully", name)

    def full_batch_migration(self, parent_folder: str, sink_schema: str, sink_nulls: str) -> None:
        files = [
            os.path.join(parent_folder, f)
            for f in os.listdir(parent_folder)
            if os.path.isfile(os.path.join(parent_folder, f))
        ]
        for file in files:
            self.batch_migration(file, sink_schema, sink_nulls)

    def streaming_load(self, table: str, df: pd.DataFrame, sink_schema: str, sink_nulls: str) -> str:
        try:
            df, df_nulls = self.get_process(table)(df, self.get_metadata(table))

            if len(df_nulls) > 0:
                df_nulls['datetime'] = datetime.now().strftime("%Y/%m/%dT%H:%M:%S")
                nulls_path = os.path.join(sink_nulls, 'streaming', f'{table}_nulls.csv')
                self._save_nulls(df_nulls, nulls_path)

            engine = self.engine()
            df.to_sql(name=table, con=engine, schema=sink_schema, if_exists='append', index=False)
            return f'{len(df)} rows inserted into table {table}'
        except KeyError:
            return f"Table '{table}' was not found in metadata"

    def query_db(self, str_sql: str) -> pd.DataFrame:
        engine = self.engine()
        return pd.read_sql(str_sql, con=engine)

    def get_num_hired_Q(self) -> str:
        df = self.query_db(queries().str_sql_count_hired_Q)
        return df.to_json(index=False, orient='records')
