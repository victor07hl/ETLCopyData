import os
import logging
import pandas as pd
import pandavro as pdx
from connections import connections

logger = logging.getLogger(__name__)

DEFAULT_BACKUP_PATH = os.getenv(
    'BACKUP_PATH',
    os.path.join(os.path.dirname(__file__), '..', 'backups')
)


class backups(connections):
    def __init__(self, path: str = DEFAULT_BACKUP_PATH) -> None:
        self.path = path

    def get_tbl_backup(self, schema: str, table: str) -> str:
        try:
            engine = self.engine()
            df = pd.read_sql(f'SELECT * FROM {schema}.{table}', con=engine)
            os.makedirs(self.path, exist_ok=True)
            tbl_path = os.path.join(self.path, table)
            pdx.to_avro(tbl_path, df)
            logger.info("Backup for %s generated at %s", table, tbl_path)
            return f'Backup for {table} was successfully generated'
        except Exception as e:
            logger.error("Backup failed for %s: %s", table, e)
            raise

    def restore_tbl_backup(self, schema: str, table: str) -> str:
        try:
            engine = self.engine()
            tbl_path = os.path.join(self.path, table)
            df = pdx.read_avro(tbl_path)
            df.to_sql(name=table, con=engine, schema=schema, if_exists='replace', index=False)
            logger.info("Table %s successfully restored", table)
            return f'Table {table} was successfully restored'
        except Exception as e:
            logger.error("Restore failed for %s: %s", table, e)
            raise
