// This JS will render a dynamic table for editing masterclass sessions and handle add/remove/save actions.
// (This is a stub; you can expand it for full CRUD with AJAX.)
document.addEventListener('DOMContentLoaded', function() {
    const app = document.getElementById('masterclass-schedule-app');
    app.innerHTML = `
      <div style="margin-bottom: 20px;">
        <button id="add-session-btn" class="add-session-btn">+ Add Session</button>
      </div>
      <form id="schedule-form">
        <table id="schedule-table" class="schedule-table">
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
        <button type="submit" class="save-schedule-btn">Save Schedule</button>
      </form>
      <style>
      .schedule-table th, .schedule-table td {
        padding: 8px 6px;
        border-bottom: 1px solid #e0e0e0;
      }
      .schedule-table input, .schedule-table select, .schedule-table textarea {
        width: 100%;
        padding: 7px 10px;
        border: 1px solid #b0bec5;
        border-radius: 5px;
        font-size: 1rem;
        background: #f8fafb;
        box-sizing: border-box;
        transition: border 0.2s;
      }
      .schedule-table input:focus, .schedule-table select:focus, .schedule-table textarea:focus {
        border: 1.5px solid #40916c;
        outline: none;
        background: #fff;
      }
      .add-session-btn {
        background: #2d6a4f;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        font-size: 1rem;
        cursor: pointer;
        margin-bottom: 8px;
      }
      .add-session-btn:hover {
        background: #40916c;
      }
      .save-schedule-btn {
        margin-top: 20px;
        background: #40916c;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 1.08rem;
        font-weight: 500;
        cursor: pointer;
      }
      .remove-session-btn {
        background: #e63946;
        color: #fff;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        font-size: 1.2rem;
        cursor: pointer;
        transition: background 0.18s;
      }
      .remove-session-btn:hover {
        background: #b71c1c;
      }
      @media (max-width: 700px) {
        .schedule-table, .schedule-table thead, .schedule-table tbody, .schedule-table tr {
          display: block;
          width: 100%;
        }
        .schedule-table thead {
          display: none;
        }
        .schedule-table tr {
          margin-bottom: 18px;
          background: #f8fafb;
          border-radius: 7px;
          box-shadow: 0 1px 4px rgba(0,0,0,0.04);
          padding: 10px 0 6px 0;
        }
        .schedule-table td {
          display: flex;
          align-items: center;
          padding: 8px 12px;
          border: none;
        }
        .schedule-table td:before {
          content: attr(data-label);
          flex: 0 0 90px;
          font-weight: 600;
          color: #40916c;
          margin-right: 8px;
          font-size: 0.98rem;
        }
        .remove-session-btn {
          margin-left: 10px;
        }
      }
      </style>
    `;
    const tbody = document.getElementById('schedule-tbody');
    function addSessionRow(session) {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td data-label="Day"><select name="day[]"><option value="1">Day 1</option><option value="2">Day 2</option></select></td>
        <td data-label="Time"><input name="time[]" placeholder="e.g. 8:00 AM" required></td>
        <td data-label="Title"><input name="title[]" placeholder="Session title" required></td>
        <td data-label="Description"><textarea name="description[]" placeholder="Short description" rows="1" style="resize:vertical;min-height:32px;max-height:180px;width:100%;overflow:auto;"></textarea></td>
        <td data-label="Remove"><button type="button" class="remove-session-btn">&times;</button></td>
      `;
      row.querySelector('.remove-session-btn').onclick = function() {
        row.remove();
      };
      // Populate values if session provided
      if (session) {
        row.querySelector('select[name="day[]"]').value = session.day;
        row.querySelector('input[name="time[]"]').value = session.time;
        row.querySelector('input[name="title[]"]').value = session.title;
        row.querySelector('textarea[name="description[]"]').value = session.description;
      }
      tbody.appendChild(row);
    }
    // Load existing sessions if present
    if (window.masterclassSessions && Array.isArray(window.masterclassSessions)) {
      window.masterclassSessions.forEach(addSessionRow);
    }
    document.getElementById('add-session-btn').onclick = function() {
      addSessionRow();
    };
    document.getElementById('schedule-form').onsubmit = function(e) {
      e.preventDefault();
      // Gather data from table
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const sessions = rows.map(row => ({
        day: row.querySelector('select[name="day[]"]').value,
        time: row.querySelector('input[name="time[]"]').value,
        title: row.querySelector('input[name="title[]"]').value,
        description: row.querySelector('textarea[name="description[]"]').value,
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
    // Auto-expand textarea for description
    app.addEventListener('input', function(e) {
      if (e.target.tagName === 'TEXTAREA') {
        e.target.style.height = 'auto';
        e.target.style.height = (e.target.scrollHeight) + 'px';
      }
    });
});
