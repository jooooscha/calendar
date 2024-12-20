import sqlite3

def init(drop=False):
    # Step 1: Connect to the database (or create it)
    conn = sqlite3.connect('calendars.db')

    # Step 2: Create a cursor object
    cur = conn.cursor()

    if drop:
        cur.execute("DROP TABLE IF EXISTS calendars")
        cur.execute("DROP TABLE IF EXISTS events")
        cur.execute("DROP TABLE IF EXISTS exdates")


    # Step 3: Create a table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS calendars (
            id TEXT PRIMARY KEY,
            visible INTEGER DEFAULT 1,
            name TEXT NOT NULL,
            color TEXT DEFAULT "gray"
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eventId TEXT NOT NULL,
            calendarId TEXT NOT NULL,
            title TEXT,
            body TEXT,
            start TEXT,
            end TEXT,
            location TEXT,
            isReadOnly TEXT,
            category TEXT,
            rrule TEXT
        )
    ''');


    cur.execute('''
        CREATE TABLE IF NOT EXISTS exdates (
            eventId TEXT NOT NULL,
            calendarId TEXT NOT NULL,
            date TEXT NOT NULL,
            PRIMARY KEY (eventId, calendarId)
        )
    ''')

    conn.commit()
    conn.close()

def add_cal(id, name, color, visible=True):
    conn = sqlite3.connect('calendars.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO calendars (id, name, color, visible) VALUES (?, ?, ?, ?)", (id, name, color, visible))
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

def add_event(
    id,
    calendar_id,
    title,
    body,
    start,
    end,
    location,
    read_only,
    category,
    rrule,
    exdates,
    conn=None,
    commit=True,
    close=True,
):
    if conn is None:
        conn = sqlite3.connect('calendars.db')

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events
            (eventId, calendarId, title, body, start, end, location, isReadOnly, category, rrule)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            id,
            calendar_id,
            title,
            body,
            start,
            end,
            location,
            read_only,
            category,
            rrule
        )
    )

    #  if exdates:
    #      for d in exdates:
    #          cur.execute("""
    #              INSERT INTO
    #                  exdates
    #                  (eventId, calendarId, date)
    #              VALUES
    #                  (?, ?, ?)
    #           """,
    #              (id, calendar_id, d)
    #          )


    if commit:
        conn.commit()
    if close:
        conn.close()

def get_events():
    conn = sqlite3.connect('calendars.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM events")
    rows = cur.fetchall()
    conn.close()
    result = [dict(row) for row in rows]
    return result

def purge():
    init(drop=True)
