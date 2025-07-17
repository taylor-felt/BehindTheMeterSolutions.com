import csv
import sqlite3
DB='rates.db'

conn=sqlite3.connect(DB)
cur=conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS states(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE)')
cur.execute('CREATE TABLE IF NOT EXISTS utilities(id INTEGER PRIMARY KEY AUTOINCREMENT,state_id INTEGER,name TEXT,FOREIGN KEY(state_id) REFERENCES states(id))')
conn.commit()

with open('Utilities.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    # skip lines until header
    for row in reader:
        if row and row[0].strip()=="State":
            headers=row
            break
    reader = csv.DictReader(f, fieldnames=headers)
    for row in reader:
        state=row['State']
        util=row['Utility Name']
        cur.execute('INSERT OR IGNORE INTO states(name) VALUES(?)',(state,))
        conn.commit()
        cur.execute('SELECT id FROM states WHERE name=?',(state,))
        state_id=cur.fetchone()[0]
        cur.execute('SELECT id FROM utilities WHERE state_id=? AND name=?',(state_id, util))
        if not cur.fetchone():
            cur.execute('INSERT INTO utilities(state_id,name) VALUES(?,?)',(state_id, util))
conn.commit()
conn.close()
print('Loaded utilities')
