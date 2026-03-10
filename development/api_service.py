import os
import logging
from flask import Flask, request, jsonify, render_template
from process_data import commun_functions
from migratedata import migratedata
from backups import backups

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

ALLOWED_TABLES = {'departments', 'hired_employees', 'jobs'}
DATA_PATH = os.getenv('DATA_PATH', os.path.join(os.path.dirname(__file__), '..', 'data'))
NULLS_PATH = os.path.join(DATA_PATH, 'nulls')
SCHEMA = os.getenv('DB_SCHEMA', 'stage')
MAX_ROWS = int(os.getenv('MAX_ROWS', 1000))


def _validate_table(table: str):
    if table not in ALLOWED_TABLES:
        return jsonify({'error': f"Table '{table}' is not allowed"}), 400
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/table/<table>', methods=['GET'])
def get_table_data(table):
    error = _validate_table(table)
    if error:
        return error
    try:
        df = migratedata().query_db(f'SELECT * FROM {SCHEMA}.{table}')
        return jsonify({'status': 'success', 'data': df.to_dict(orient='records')}), 200
    except Exception as e:
        logger.error("Query failed for table %s: %s", table, e)
        return jsonify({'error': str(e)}), 500


@app.route('/test', methods=['POST'])
def test_connection():
    return jsonify({'status': 'success'}), 200


@app.route('/insert/<table>', methods=['POST'])
def insert_data(table):
    error = _validate_table(table)
    if error:
        return error
    try:
        raw_data = request.get_data()
        df = commun_functions().strjson2pd_df(raw_data)
        if df is None:
            return jsonify({'error': 'Empty payload'}), 400
        rows, cols = df.shape
        if not (0 < rows < MAX_ROWS and cols > 0):
            return jsonify({'error': f'{rows} rows rejected: must be between 1 and {MAX_ROWS}'}), 400
        message = migratedata().streaming_load(table, df, SCHEMA, NULLS_PATH)
        return jsonify({'status': 'success', 'message': message}), 200
    except Exception as e:
        logger.error("Insert failed for table %s: %s", table, e)
        return jsonify({'error': str(e)}), 500


@app.route('/fullmigrate', methods=['POST'])
def full_migrate():
    try:
        migratedata().full_batch_migration(
            parent_folder=DATA_PATH,
            sink_schema=SCHEMA,
            sink_nulls=NULLS_PATH,
        )
        return jsonify({'status': 'success', 'message': 'Full load completed'}), 200
    except Exception as e:
        logger.error("Full migration failed: %s", e)
        return jsonify({'error': str(e)}), 500


@app.route('/backup/<table>', methods=['POST'])
def backup_tbl(table):
    error = _validate_table(table)
    if error:
        return error
    try:
        message = backups().get_tbl_backup(SCHEMA, table)
        return jsonify({'status': 'success', 'message': message}), 200
    except Exception as e:
        logger.error("Backup failed for table %s: %s", table, e)
        return jsonify({'error': str(e)}), 500


@app.route('/restore/<table>', methods=['POST'])
def restore_table(table):
    error = _validate_table(table)
    if error:
        return error
    try:
        message = backups().restore_tbl_backup(SCHEMA, table)
        return jsonify({'status': 'success', 'message': message}), 200
    except Exception as e:
        logger.error("Restore failed for table %s: %s", table, e)
        return jsonify({'error': str(e)}), 500


@app.route('/getNumHired', methods=['GET'])
def get_num_hired():
    try:
        output = migratedata().get_num_hired_Q()
        return jsonify({'status': 'success', 'message': output}), 200
    except Exception as e:
        logger.error("Query failed: %s", e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
