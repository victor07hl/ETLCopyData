#from connections import connections
import pandas as pd
import os 
from process_data import proccess_data
from connections import connections
from datetime import datetime

class migratedata(proccess_data,connections):
    def __init__(self) -> None:
        pass

    def batch_migration(self,file:str,sink_schema:str,sink_nulls:str) -> str:
        df,name = self.read_data_source(file)
        Trans_data = self.get_process(name)
        df, df_nulls = Trans_data(df,self.get_metadata(name))
            
        #verify that the folder exits
        sink_nulls = os.path.join(sink_nulls,'batch')
        if os.path.isdir(sink_nulls) != True:
            os.makedirs(sink_nulls)

        nulls_path = os.path.join(sink_nulls,name+'_nulls.csv')
        if len(df_nulls)> 0:
            df_nulls.to_csv(nulls_path,index=False) 
            print(nulls_path,'saved')

        engine = self.engine()
        df.to_sql(name=name, con=engine, schema= sink_schema, if_exists = 'replace',index=False)
        print(f'table {name}, was loaded!')
    
    def full_batch_migration(self, parent_folder:str,sink_schema:str, sink_nulls:str) :
        files = [os.path.join(parent_folder,file)  for file in os.listdir(parent_folder)]
        files = [file for file in files if os.path.isdir(file)!=True]
        for file in files:
            self.batch_migration(file,sink_schema,sink_nulls)

    def get_metadata(self,source_name) -> dict:
        schema = {'departments':{'id':int,'department':str},
                  'hired_employees':{'id':int,'name':str,'DATETIME':str,'department_id':int,'job_id':int},
                  'jobs':{'id':int,'job':str}} 
        return schema[source_name]
        
    def streaming_load(self,table,df,sink_schema,sink_nulls):
        try:
            Trans_data = self.get_process(table)
            df, df_nulls = Trans_data(df,self.get_metadata(table))
            sink_nulls = os.path.join(sink_nulls,'streaming')
            print(sink_nulls)
            if os.path.isdir(sink_nulls) != True:
                os.makedirs(sink_nulls)

            nulls_path = os.path.join(sink_nulls,table+'_nulls.csv')
            if len(df_nulls)> 0:
                df_nulls['datetime'] = datetime.now().strftime("%Y/%m/%dT%H:%M:%S")
                try:
                    df_nulls.to_csv(nulls_path,index=False,mode='x') 
                except FileExistsError as e:
                    df_nulls.to_csv(nulls_path,index=False,mode='a',header=False) 
                print(nulls_path,'saved')

            engine = self.engine()
            df.to_sql(name=table, con=engine, schema= sink_schema, if_exists = 'append',index=False)
        except KeyError as e:
            return f'table {table} was not found on metadata'
        return f'{len(df)} rows was inserted on table {table}'

        



    def read_data_source(self,source:str):
        extension = os.path.split(source)[1]
        name = extension.split('.')[0]
        extension = extension.split('.')[1]
        if extension == 'xlsx':
            df = pd.read_excel(source,header=None)
        elif extension == 'csv':
            df = pd.read_csv(source,header=None)

        schema = self.get_metadata(name)
        columns = list(schema.keys())
        df.columns = columns
        #df = df.astype(schema)
        return df,name

if __name__ == '__main__':
    migrate = migratedata()
    #path = r"C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\hired_employees.xlsx"
    #df = migrate.read_data_source(path)
    #print(df.head())