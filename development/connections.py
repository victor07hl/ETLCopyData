import os
import logging
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

try:
    from credentials import msql_user, msql_pwd, db, server_ip
except ImportError:
    msql_user = os.getenv('DB_USER', '')
    msql_pwd = os.getenv('DB_PWD', '')
    db = os.getenv('DB_NAME', '')
    server_ip = os.getenv('DB_SERVER', '')


class connections:
    def engine(self):
        connection_string = (
            f'mssql+pyodbc://{msql_user}:{msql_pwd}@{server_ip}/{db}'
            f'?driver=ODBC+Driver+17+for+SQL+Server'
        )
        return create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
