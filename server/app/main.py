from flask import Flask, jsonify
import app.db as db
from dotenv import load_dotenv
from app.event_helper import *
from app import dav


# remove ctrl+c traceback
import signal
import sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

app = Flask(__name__)

@app.route('/caldav/calendars')
def get_calendars():
    data = db.get_calendars()
    print("Calendars in DB", len(data))
    cals = [
        {
            "id": r[0],
            "visible": r[1],
            "name": r[2],
            "backgroundColor": r[3],
        }
        for r in data
    ]

    return jsonify(cals)

@app.route('/caldav/events')
def get_caldav_events():
    print("Events requested")
    events = db.get_events()

    return events

@app.route('/caldav/toggle/<cal_id>')
def toggle_calendar(cal_id):
    visible = db.get_visible(cal_id)
    db.set_visible(cal_id, not visible)
    ret = {
        "error": False,
        "visible": not visible,
    }
    return jsonify(ret)

@app.route('/caldav/toggle_all/<state>')
def toggle_calendar_all(state):
    state = True if state == "true" else False
    db.set_visibility_all(state)
    ret = {
        "error": False,
    }
    return jsonify(ret)

@app.route('/caldav/sync')
def sync_calendar():
    x = dav.sync_data()
    if x is None:
        ret = { "error": False, }
    else:
        ret = { "error": True, }
    return jsonify(ret)



def main():
    load_dotenv("./.env")
    print("Connect to DAV")
    dav.init(sync=False)
    print("Running server...")
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    main()
