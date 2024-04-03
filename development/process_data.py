import re
class commun_functions():
    def __init__(self) -> None:
        pass

    def str_to_int(self,str_number:str) -> int:
        str_number = str(str_number)
        str_number = str_number.split('.')[0]
        if str_number.isnumeric():
            int_number = int(str_number)
        else:
            int_number = 'NoNumber'
        return int_number
    

class proccess_data(commun_functions):
    def __init__(self) -> None:
        pass

    def process_hired(self,df,schema=None):
        #schema : 'departments' -> {'id':int,'department':str}
        df_nulls = df.isna().any(axis=1)
        df_nulls = df[df_nulls]
        df = df.copy()
        df = df.dropna()
        
        df['department_id'] = df['department_id'].apply(self.str_to_int)
        df['job_id'] = df['job_id'].apply(self.str_to_int)
        df_invalid_format = df[(df['department_id']=='NoNumber') | (df['job_id']=='NoNumber')]
        df = df[(df['department_id']!='NoNumber') & (df['job_id']!='NoNumber')]

        #casting cols
        for col in schema.keys():
            df[col] = df[col].astype(schema[col])

        
        return df,df_nulls,df_invalid_format



    
if __name__ == '__main__':
    comun = commun_functions()
    from migratedata import migratedata
    migrate = migratedata()
    path = r"C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\hired_employees.xlsx"
    df,name = migrate.read_data_source(path)
    
    proccess_data = proccess_data()
    df_new,nulls,invalid_format = proccess_data.process_hired(df,migrate.get_metadata(name))
    print(df_new.head())
    print(nulls[nulls['id']==162].head())


