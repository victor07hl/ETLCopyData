#from connections import connections
import pandas as pd
import os 

class migratedata():
    def __init__(self) -> None:
        pass

    def batch(self,source:str,sink:str) -> str:
        pass

    def get_metadata(self,source_name) -> dict:
        schema = {'departments':{'id':int,'department':str},
                  'hired_employees':{'id':int,'name':str,'DATETIME':str,'department_id':int,'job_id':int},
                  'jobs':{'id':int,'job':str}} 
        return schema[source_name]
        
        


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
    path = r"C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\hired_employees.xlsx"
    df = migrate.read_data_source(path)
    print(df.head())