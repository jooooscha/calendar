import { $, CalButton, Manager } from "./manager.js"

const manager = new Manager();

manager.update()

function butttonSuccessAnimation(btn, success) {
    btn.classList.remove('btn-secondary');

    let btnclass;
    if (success) {
        btnclass = "btn-success"
    } else {
        btnclass = "btn-danger"
    }
    btn.classList.add(btnclass);

    // After 3 seconds, revert the button back to the original color
    setTimeout(() => {
        btn.classList.remove(btnclass);
        btn.classList.add('btn-secondary');
    }, 3000)
}

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

$('.allOn').addEventListener('click', () => manager.toggleAll(true) );
$('.allOff').addEventListener('click', () => manager.toggleAll(false) );

$('.syncbtn').addEventListener('click', () =>  sync() )

async function sync() {
    let syncbtn = $('.syncbtn')
    syncbtn.disable = true
    syncbtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Syncing ...`;
    try {
        await fetch("http://localhost:5000/caldav/sync")
            .then(response => {
                return response.text()
            }).then(text => {
                let ret = JSON.parse(text)
                console.log("ret:", ret)
            })
        butttonSuccessAnimation(syncbtn, true)
    } catch (error) {
        console.log("Could not finisch update: " + error)
        butttonSuccessAnimation(syncbtn, false)
    } finally {
        syncbtn.disable = false
        syncbtn.innerHTML = 'Sync';
        manager.update()
    }
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
