import sqlite3

def init():
    # Step 1: Connect to the database (or create it)
    conn = sqlite3.connect('calendars.db')

    # Step 2: Create a cursor object
    cur = conn.cursor()

    # Step 3: Create a table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS calendars (
            id TEXT PRIMARY KEY,
            visible INTEGER DEFAULT 1,
            name TEXT NOT NULL,
            color TEXT DEFAULT "gray"
        )
    ''')

    conn.commit()
    conn.close()

def add_cal(id, name, color, visible=True):
    conn = sqlite3.connect('calendars.db')
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO calendars (id, name, color, visible) VALUES (?, ?, ?, ?)", (id, name, color, visible))
    conn.commit()
    conn.close()

def get_calendars():
    conn = sqlite3.connect('calendars.db')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM calendars")
    all = cur.fetchall()
    conn.close()
    return all

def get_visible(cal_id):
    conn = sqlite3.connect('calendars.db')
    cur = conn.cursor()
    cur.execute(f"SELECT visible FROM calendars WHERE id = ?", (cal_id,))
    visible = cur.fetchone()[0]
    conn.close()
    return True if visible == 1 else False

def set_visible(cal_id, visible):
    value = visible
    conn = sqlite3.connect('calendars.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE calendars SET visible = ? WHERE id = ?", (value, cal_id))
    conn.commit()
    conn.close()
    return visible

def set_visibility_all(state):
    conn = sqlite3.connect('calendars.db')
    cur = conn.cursor()
    cur.execute(f"UPDATE calendars SET visible = ?", (state,))
    conn.commit()
    conn.close()
