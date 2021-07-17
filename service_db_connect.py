import sqlite3

def connect_db():
    conn = sqlite3.connect("service.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS ticket (id INTEGER PRIMARY KEY, date TEXT NOT NULL, tr TEXT NOT NULL, wo TEXT, cust TEXT NOT NULL, addr TEXT NOT NULL, issue TEXT NOT NULL, notes TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, site TEXT, part TEXT, desc TEXT, qty INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS cust_info (id INTEGER PRIMARY KEY, cust_name TEXT, cust_notes TEXT NOT NULL)")
    conn.commit()
    conn.close()
    
connect_db()