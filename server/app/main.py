import caldav
import caldav.elements.ical # for calendarColor
from flask import Flask, jsonify
from dataclasses import dataclass, asdict
import random
import json
import app.db as db
from dotenv import load_dotenv
import os

# remove ctrl+c traceback
import signal
import sys
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

load_dotenv()

app = Flask(__name__)

event_map = {}

def init():
    global calendar_list
    global event_map

    db.init()

    # CalDAV server details
    url = os.getenv('SERVER_URL')
    username = os.getenv("USER")
    password = os.getenv("PASSWORD")

    # Connect to the CalDAV server
    try:
        client = caldav.DAVClient(url, username=username, password=password)
    except:
        return 404
    principal = client.principal()
    calendars = principal.calendars()

    if not calendars:
        return jsonify({"error": "No calendars found"}), 404
    else:
        for cal in calendars:

            color = cal.get_property(caldav.elements.ical.CalendarColor())
            db.add_cal(cal.id, cal.name, color, visible=True)

            events = []
            for event in cal.events():
                for component in event.icalendar_instance.walk():
                    if component.name == "VEVENT":
                        events.append(prepare(component, cal.id))

            event_map[cal.id] = events

def prepare(component, calId):

    match component.get("dtstart").params.get("value"):
        case "DATE":
            category = "allday"
        case _:
            category = "time"

    event = {
        "id": component.get("uid"),
        "calendarId": calId,
        "title": component.get("summary"),
        "body": component.get("description"),
        "start": component.get("dtstart").dt.strftime("%Y-%m-%dT%H:%M"),
        #  "end": component.get("dtend").dt.strftime("%Y-%m-%dT%H:%M"),
        "location": component.get("location"),
        "isReadOnly": True, # TODO:
        "category": category
    }

    endDate = component.get("dtend")
    if endDate and endDate.dt:
        event["end"] = endDate.dt.strftime("%Y-%m-%dT%H:%M")
    else:
        event["end"] = event["start"]

    return event

@app.route('/caldav/calendars')
def get_calendars():
    data = db.get_calendars()
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
    events = [item for sublist in event_map.values() for item in sublist]
    return jsonify(events)

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


def main():
    print("Connect to DAV")
    init()
    print("Running server...")
    app.run(debug=True)

if __name__ == '__main__':
    main()
