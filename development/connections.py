from sqlalchemy import create_engine
from credentials import msql_user, msql_pwd, db, server_ip
class connections:
    def __init__(self) -> None:
        pass

    def engine(self):
        driver = '{ODBC Driver 17 for SQL Server}'
        #str_connect = 'DRIVER='+driver+';Server='+server_ip+'; Database='+db+';UID='+msql_user+';PWD='+ msql_pwd
        str_connect = f'mssql+pyodbc://{msql_user}:{msql_pwd}@{server_ip}/{db}?driver=ODBC Driver 17 for SQL Server'
        #print(str_connect)
        #cnxn = pyodbc.connect(str_connect)
        cnxn = create_engine(str_connect)
        
        return cnxn


