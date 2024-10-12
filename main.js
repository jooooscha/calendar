import { $, CalButton, Manager } from "./manager.js"

const manager = new Manager();

manager.update()

// implement the buttons
var weekButton = $('.week');
weekButton.addEventListener('click', function () {
    manager.changeView("week");
});
var weekButton = $('.month');
weekButton.addEventListener('click', function () {
    manager.changeView("month");
});
var weekButton = $('.multi-week');
weekButton.addEventListener('click', function () {
    manager.changeView("multi-week");
});

var nextButton = $('.next');
nextButton.addEventListener('click', function () {
    manager.next();
});

var prevButton = $('.prev');
prevButton.addEventListener('click', function () {
    manager.prev();
});

var prevButton = $('.today');
prevButton.addEventListener('click', function () {
    manager.today();
});

var all_off_button = $('.all_off');
all_off_button.addEventListener('click', function () {
    manager.toggleAll(false);
});

var all_on_button = $('.all_on');
all_on_button.addEventListener('click', function () {
    manager.toggleAll(true);
});
$('.syncbtn').addEventListener('click', () => sync())

async function sync() {
    await fetch("http://localhost:5000/caldav/sync")
        .then(response => {
            return response.text()
        }).then(text => {
            let ret = JSON.parse(text)
            console.log("ret:", ret)
        })
}

//init sync of calendars
async function init_calendars() {
    await fetch("http://localhost:5000/caldav/calendars")
        .then(response => {
            return response.text()
        }).then(text => {
            let cals = JSON.parse(text)
            manager.addCals(cals)
        })
}

function fetch_events() {
    fetch("http://localhost:5000/caldav/events").then(response => {
        return response.text()
    }).then(text => {
            let events = JSON.parse(text)
            manager.addEvents(events)
        })
}

init_calendars().then(() => {
    fetch_events()
})
