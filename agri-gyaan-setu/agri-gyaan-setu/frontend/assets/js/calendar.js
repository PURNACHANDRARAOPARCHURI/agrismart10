/* Simple calendar widget for the dashboard

Endpoints used:
- GET /api/calendar/?month=MM&year=YYYY             -> list events in month
- POST /api/calendar/                                 -> create event
- GET /api/calendar/<id>/                              -> get/update/delete event

This file expects `window.api` helper to exist for making API calls. If not present,
it falls back to fetch() calls.
*/

(function () {
    // helper to read csrf token from cookie (Django's default name)
    function getCookie(name) {
        const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    const defaultHeaders = {'Content-Type':'application/json'};
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) defaultHeaders['X-CSRFToken'] = csrftoken;

    // Use app-provided api.fetch if available, otherwise use fetch with credentials and default headers
    const apiFetch = window.api && window.api.fetch ? window.api.fetch : (url, opts = {}) => {
        opts.credentials = opts.credentials || 'same-origin';
        opts.headers = Object.assign({}, defaultHeaders, opts.headers || {});
        return fetch(url, opts);
    };

    // expose helper functions for FullCalendar integration
    async function createEvent(payload){
        const res = await apiFetch('/api/calendar/', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        if (!res.ok) throw new Error('Failed to create event');
        return await res.json();
    }

    async function updateEvent(id, payload){
        const res = await apiFetch(`/api/calendar/${id}/`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
        if (!res.ok) throw new Error('Failed to update event');
        return await res.json();
    }

    async function deleteEvent(id){
        const res = await apiFetch(`/api/calendar/${id}/`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete event');
        return true;
    }

    window.calendarAdapter = { createEvent, updateEvent, deleteEvent };
})();
