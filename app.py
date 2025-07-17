from flask import Flask, request, jsonify, send_file
import sqlite3
import os
import pandas as pd
from io import BytesIO

DB = 'rates.db'
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS states(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS utilities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state_id INTEGER,
        name TEXT,
        FOREIGN KEY(state_id) REFERENCES states(id)
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS rate_schedules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utility_id INTEGER,
        name TEXT,
        status TEXT,
        details TEXT,
        FOREIGN KEY(utility_id) REFERENCES utilities(id)
    )''')
    conn.commit()
    conn.close()

@app.route('/initdb')
def initdb_route():
    init_db()
    return 'Database initialized'

@app.route('/api/states')
def states():
    conn = get_db_connection()
    states = conn.execute('SELECT * FROM states ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(row) for row in states])

@app.route('/api/utilities')
def utilities():
    state_id = request.args.get('state_id')
    conn = get_db_connection()
    if state_id:
        utils = conn.execute('SELECT * FROM utilities WHERE state_id=? ORDER BY name', (state_id,)).fetchall()
    else:
        utils = conn.execute('SELECT * FROM utilities ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(row) for row in utils])

@app.route('/api/rate_schedules')
def rate_schedules():
    util_id = request.args.get('utility_id')
    conn = get_db_connection()
    if util_id:
        rs = conn.execute('SELECT * FROM rate_schedules WHERE utility_id=? ORDER BY name', (util_id,)).fetchall()
    else:
        rs = conn.execute('SELECT * FROM rate_schedules ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rs])

@app.route('/api/rate_schedule/<int:sched_id>', methods=['GET', 'PUT'])
def rate_schedule(sched_id):
    conn = get_db_connection()
    if request.method == 'GET':
        row = conn.execute('SELECT * FROM rate_schedules WHERE id=?', (sched_id,)).fetchone()
        conn.close()
        if row:
            return jsonify(dict(row))
        return jsonify({'error': 'Not found'}), 404
    else:
        data = request.get_json()
        conn.execute('UPDATE rate_schedules SET name=?, status=?, details=? WHERE id=?',
                     (data['name'], data['status'], data.get('details','{}'), sched_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'updated'})

@app.route('/api/rate_schedule', methods=['POST'])
def create_rate_schedule():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO rate_schedules (utility_id, name, status, details) VALUES (?, ?, ?, ?)',
                (data['utility_id'], data['name'], data['status'], data.get('details','{}')))
    conn.commit()
    sched_id = cur.lastrowid
    conn.close()
    return jsonify({'id': sched_id})

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file', 400
    f = request.files['file']
    df = pd.read_excel(f)
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    for _, row in df.iterrows():
        state = row['State']
        util = row['Utility']
        name = row['Schedule']
        status = row.get('Status','Active')
        details = row.drop(['State','Utility','Schedule','Status']).to_json()
        # get state id
        cur.execute('INSERT OR IGNORE INTO states(name) VALUES(?)', (state,))
        conn.commit()
        cur.execute('SELECT id FROM states WHERE name=?', (state,))
        state_id = cur.fetchone()['id']
        cur.execute('INSERT OR IGNORE INTO utilities(state_id,name) VALUES(?,?)', (state_id, util))
        conn.commit()
        cur.execute('SELECT id FROM utilities WHERE name=? AND state_id=?', (util, state_id))
        util_id = cur.fetchone()['id']
        cur.execute('INSERT INTO rate_schedules (utility_id,name,status,details) VALUES(?,?,?,?)',
                    (util_id, name, status, details))
    conn.commit()
    conn.close()
    return 'Uploaded'

@app.route('/api/template')
def template():
    # Provide an Excel template
    cols = ['State','Utility','Schedule','Status','Description']
    df = pd.DataFrame(columns=cols)
    output = BytesIO()
    df.to_excel(output,index=False)
    output.seek(0)
    return send_file(output, download_name='template.xlsx', as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
