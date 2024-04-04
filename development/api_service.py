from flask import Flask, request, jsonify
from process_data import commun_functions
from migratedata import migratedata
from backups import backups

app = Flask(__name__)

@app.route('/test',methods=['POST'])
def test_connection():
    return jsonify({'status':'success'}, 200)

@app.route('/insert/<table>', methods = ['POST'])
def insert_data(table):
    if request.method == 'POST':
        raw_data = request.get_data()
        commun_f = commun_functions()
        df = commun_f.strjson2pd_df(raw_data)
        rows,cols = df.shape
        if rows>0 and rows<1000 and cols>0:
            migrate = migratedata()
            path_nulls = r'C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\nulls'
            stream2sql = migrate.streaming_load(table,df,'stage',path_nulls)
        else:
            stream2sql = f'{len(df)} rows was not loaded on table {table}. Exeption 1-1000 rows'
    return jsonify({'connection':'success','message':stream2sql})

@app.route('/fullmigrate',methods = ['GET'])
def full_migrate():
    migrate = migratedata()
    parent_folder = r'C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data'
    sink_nulls = r'C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\nulls'
    migrate.full_batch_migration(parent_folder=parent_folder,
                                 sink_schema='stage',
                                 sink_nulls=sink_nulls)
    return jsonify({'connection':'success','message':'full load has been completed'})

@app.route('/backup/<table>',methods = ['GET'])
def backup_tbl(table):
    tbl_backup = backups()
    get_tbl_backup = tbl_backup.get_tbl_backup('stage',table)
    return jsonify({'connection':'success','message':get_tbl_backup})

@app.route('/restore/<table>',methods = ['GET'])
def restore_table(table):
    tbl_backup = backups()
    restore_tbl = tbl_backup.restore_tbl_backup('stage',table)
    return jsonify({'connection':'success','message':restore_tbl})

if __name__ == '__main__':
    app.run(debug=True)