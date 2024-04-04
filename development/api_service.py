from flask import Flask, request, jsonify
from process_data import commun_functions
from migratedata import migratedata

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
        if len(df)>0 and len(df)<1000:
            migrate = migratedata()
            path_nulls = r'C:\Users\USUARIO\Desktop\Developments\ETLCopyData\data\nulls'
            stream2sql = migrate.streaming_load(table,df,'stage',path_nulls)
        else:
            stream2sql = f'{len(df)} rows was not loaded on table {table}. Exeption 1-1000 rows'
    return jsonify({'connection':'sucess','message':stream2sql})

if __name__ == '__main__':
    app.run(debug=True)