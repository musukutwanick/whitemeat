// This JS will render a dynamic table for editing masterclass sessions and handle add/remove/save actions.
// (This is a stub; you can expand it for full CRUD with AJAX.)
document.addEventListener('DOMContentLoaded', function() {
    const app = document.getElementById('masterclass-schedule-app');
    app.innerHTML = `
      <div style="margin-bottom: 20px;">
        <button id="add-session-btn" style="background: #2d6a4f; color: white; border: none; padding: 8px 16px; border-radius: 5px;">+ Add Session</button>
      </div>
      <form id="schedule-form">
        <table id="schedule-table" style="width:100%; border-collapse: collapse;">
          <thead>
            <tr>
              <th>Day</th>
              <th>Time</th>
              <th>Title</th>
              <th>Description</th>
              <th>Remove</th>
            </tr>
          </thead>
          <tbody id="schedule-tbody">
          </tbody>
        </table>
        <button type="submit" style="margin-top: 20px; background: #40916c; color: white; border: none; padding: 10px 20px; border-radius: 5px;">Save Schedule</button>
      </form>
    `;
    const tbody = document.getElementById('schedule-tbody');
    document.getElementById('add-session-btn').onclick = function() {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><select name="day[]"><option value="1">Day 1</option><option value="2">Day 2</option></select></td>
        <td><input name="time[]" placeholder="e.g. 8:00 AM" required></td>
        <td><input name="title[]" placeholder="Session title" required></td>
        <td><input name="description[]" placeholder="Short description"></td>
        <td><button type="button" class="remove-session-btn">&times;</button></td>
      `;
      row.querySelector('.remove-session-btn').onclick = function() {
        row.remove();
      };
      tbody.appendChild(row);
    };
    // Optionally: Load existing sessions via AJAX and populate rows here.
    document.getElementById('schedule-form').onsubmit = function(e) {
      e.preventDefault();
      // Gather data from table
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const sessions = rows.map(row => ({
        day: row.querySelector('select[name="day[]"]').value,
        time: row.querySelector('input[name="time[]"]').value,
        title: row.querySelector('input[name="title[]"]').value,
        description: row.querySelector('input[name="description[]"]').value,
      }));
      fetch('/dashboard/masterclass-schedule/save/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]')||{}).value || ''
        },
        body: JSON.stringify({sessions})
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          alert('Schedule saved!');
        } else {
          alert('Error: ' + (data.error || 'Could not save.'));
        }
      })
      .catch(() => alert('Network error.'));
    };
});
