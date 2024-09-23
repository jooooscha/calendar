import caldav
import caldav.elements.ical # for calendarColor
from flask import Flask, jsonify
from dataclasses import dataclass, asdict
import random
import json
import app.db as db
from dotenv import load_dotenv
import os

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
                        events.append(prepare(component))

            event_map[cal.id] = events

def prepare(component):
    event = {
        "id": component.get("uid"),
        "title": component.get("summary"),
        "start": component.get("dtstart").dt.strftime("%Y-%m-%dT%H:%M"),
        "datestamp": component.get("dtstamp").dt.strftime("%Y-%m-%dT%H:%M"),
        "body": "Body",
        "isAllday": True,
    }
    endDate = component.get("dtend")
    if endDate and endDate.dt:
        event["end"] = endDate.dt.strftime("%Y-%m-%dT%H:%M")
    #  print(event)
    return event

@app.route('/caldav/calendars')
def get_calendars():
    data = db.get_calendars()
    cals = [
        {
            "id": r[0],
            "visible": r[1],
            "name": r[2],
            "backrgoundColor": r[3],
        }
        for r in data
    ]

    return jsonify(cals)

@app.route('/caldav/events')
def get_caldav_events():

    ret = []
    for cal_id, events in event_map.items():
        for e in events:
            e["calendarId"] = cal_id
        ret.extend(events)

    return jsonify(ret)

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
