export const $ = function (selector) {
    return document.querySelector(selector);
}

export class Manager {
    constructor() {
        this.tuiCal = new tui.Calendar('#calendar', {
            defaultView: 'month', // Can be 'day', 'week', or 'month'
            useCreationPopup: true, // Enable popup for creating events
            useDetailPopup: true, // Enable popup for event details
            useFormPopup: true,
            isReadOnly: true,
            usageStatistics: false,
            month: {
                visibleWeeksCount: 5,
                startDayOfWeek: 1,
                narrowWeekend: false,
                visibleEventCount: 6,
            },
            week: {
                startDayOfWeek: 1,
            },
            calendars: [
                // {
                //     id: '1',
                //     name: 'Personal Calendar',
                //     backgroundColor: '#9e5fff',
                //     borderColor: '#9e5fff',
                // }
            ],
        });

        this.cals = {}
    }
    next() {
        this.tuiCal.next();
        this.update()
    }
    prev() {
        this.tuiCal.prev();
        this.update()
    }
    changeView(view) {
        if (view == "week") {
            this.tuiCal.changeView("week");
        } else if (view == "month") {
            this.tuiCal.changeView("month");
            this.tuiCal.setOptions({
                month: {
                    visibleWeeksCount: 0,
                },
            });
        } else if (view == "multi-week") {
            this.tuiCal.changeView("month");
            this.tuiCal.setOptions({
                month: {
                    visibleWeeksCount: 5,
                },
            });
        }
        this.update()
    }
    update() {
        $('.range').innerHTML = this.tuiCal.renderRange.start;
    }
    addCals(cals) {
        this.tuiCal.setCalendars(cals)
        for (let cal of cals) {
            let id = cal.id;
            let tuiCal = this.tuiCal
            const callback = function(b) {
                // hide calendar
                tuiCal.setCalendarVisibility(cal.id, b)
            }
            let button = new CalButton(cal.id, cal.name, cal.visible, callback);
            console.log("button:", button)
            this.cals[id] = button
            $("#calendar-list").appendChild(button.export());
        }
    }
    toggleAll(bool) {
        fetch("http://localhost:5000/caldav/toggle_all/" + bool)
            .then(response => {
                return response.text()
            })

        for (let id in this.cals) {
            let cal = this.cals[id]
            console.log(cal)
            this.tuiCal.setCalendarVisibility(cal.id, bool)
        }
        let cals = $("#calendar-list").children
        for (let cal of cals) {
            cal.children[0].checked = bool
        }
    }
    addEvents(events) {
        this.tuiCal.createEvents(events)
    }
}

export class CalButton {
    constructor(id, name, b, onclickCallback) {
        this.id = id;
        this.name = name;
        this.checked = b;
        this.callback = onclickCallback;
    }

    export() {
        let li = document.createElement("li");
        // create checkbox
        let checkbox = document.createElement("input");

        let id = this.id
        let callback = this.callback

        checkbox.type = "checkbox";
        checkbox.checked = this.checked;
        checkbox.onclick = function(event) {
            event.preventDefault()
            // toggle calendar in backend and call callback
            fetch("http://localhost:5000/caldav/toggle/" + id)
                .then(resp => resp.text())
                .then(v => {
                    v = JSON.parse(v)
                    this.checked = v.visible
                    callback(v.visible)
                })
        }

        let span = document.createElement("span")
        span.textContent = this.name

        li.appendChild(checkbox)
        li.appendChild(span)

        return li
    }
}

export const createCalButton = function() {
    // let li = document.createElement("li");
    // let checkbox = document.createElement("input");
    // checkbox.type = "checkbox";

    // let span = document.createElement("span")
    // // span.textContent = cal.name
    // // checkbox.onclick = function() {
    //     // if (cal.id in visibility) {
    //     //     tuiCal.setCalendarVisibility(cal.id, )
    //     // }
    // // }
    // li.appendChild(checkbox)
    // li.appendChild(span)
    // // li.textContent = calName
    // // $("#calendar-list").appendChild(li);
    return li
}
