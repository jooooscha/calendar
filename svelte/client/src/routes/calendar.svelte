<script>
  import { onMount } from 'svelte';
  import { fetch_events, fetch_calendars } from '$lib/index.ts';

  let calendar;
  let Calendar;
  let calendarOptions = {
            defaultView: 'month', // Can be 'day', 'week', or 'month'
            useCreationPopup: true, // Enable popup for creating events
            useDetailPopup: true, // Enable popup for event details
            useFormPopup: true,
            isReadOnly: true,
            usageStatistics: false, // disable google spyware
            month: {
                visibleWeeksCount: 6,
                startDayOfWeek: 2,
                narrowWeekend: false,
                visibleEventCount: 6,
            },
            week: {
                startDayOfWeek: 1,
                taskView: ["task"],
            },
            calendars: [ ],
  };


  // Initialize calendar only on the client side
  onMount(async () => {
    const { default: CalendarLib } = await import('@toast-ui/calendar');
    Calendar = CalendarLib;

    calendar = new Calendar(document.getElementById('calendar'), calendarOptions);

    let cals = await fetch_calendars();
    calendar.setCalendars(cals);

    let events = await fetch_events();
    calendar.createEvents(events);

  });

  function setWeek() {
    calendar.changeView("week");
  }
</script>

<style>
@import "https://uicdn.toast.com/calendar/latest/toastui-calendar.min.css";

#calendar {
    width: 100%;
    height: 500px;
    border: 1px solid #eee;
}

</style>


<button onclick={setWeek}>Week</button>
<div id="calendar"></div>
