#from connections import connections
import pandas as pd
import os 
from process_data import proccess_data

class migratedata(proccess_data):
    def __init__(self) -> None:
        pass

    def batch_migration(self,parent_folder:str,sink:str,sink_nulls:str) -> str:
        files = [os.path.join(parent_folder,file) for file in os.listdir(parent_folder)]
        for file in files:
            df,name = self.read_data_source(file)
            Trans_data = self.get_process(name)
            df, df_nulls = Trans_data(df,self.get_metadata(name))
            nulls_path = os.path.join(sink_nulls,name+'_nulls.csv')
            df_nulls.to_csv(nulls_path,index=False)
            print(nulls_path,'saved')


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
    #path = r"C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\hired_employees.xlsx"
    #df = migrate.read_data_source(path)
    #print(df.head())
    parent_folder = r'C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data'
    sink_nulls = r'C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\nulls'
    migrate.batch_migration(parent_folder,'jsjs',sink_nulls)