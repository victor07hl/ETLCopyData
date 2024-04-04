from connections import connections
import pandas as pd
import pandavro  as pdx
import os 
class backups(connections):
    def __init__(self,path=r"C:\Users\USUARIO\Desktop\Developments\ETLCopyData\backups") -> None:
        self.path = path
        pass

    def get_tbl_backup(self,schema,table):
        engine = self.engine()
        df = pd.read_sql(f'select * from {schema}.{table}',con=engine)
        tbl_path = os.path.join(self.path,table)
        pdx.to_avro(tbl_path,df)
        return f'backup for {table} was succesfully generated'
    
    def restore_tbl_backup(self,schema,table):
        engine = self.engine()
        tbl_path = os.path.join(self.path,table)
        df = pdx.read_avro(tbl_path)
        df.to_sql(name=table, con=engine, schema= schema, if_exists = 'replace',index=False)
        return f'table {table} was successfully restored'

if __name__=='__main__':
    tbl_backup = backups()
    #tbl_backup.get_tbl_backup('stage','jobs')
    tbl_restore = tbl_backup.restore_tbl_backup('stage','jobs')
