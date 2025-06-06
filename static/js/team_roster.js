document.querySelectorAll('.cut-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        const playerName = btn.getAttribute('data-player-name');
        const playerId = btn.getAttribute('data-player-id');
        if (confirm(`Are you sure you want to cut ${playerName}?`)) {
            // Create and submit a form dynamically
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/cut_player/{{team_id}}';
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'player_id';
            input.value = playerId;
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        }
    });
});

// Filter and search functionality
document.getElementById('player-search').addEventListener('input', filterRosterTable);
document.getElementById('position-filter').addEventListener('change', filterRosterTable);
document.getElementById('trade-status-filter').addEventListener('change', filterRosterTable);

function filterRosterTable() {
    const search = document.getElementById('player-search').value.toLowerCase();
    const position = document.getElementById('position-filter').value;
    const tradeStatus = document.getElementById('trade-status-filter').value;
    document.querySelectorAll('#roster-table tbody tr').forEach(function(row) {
        const name = row.cells[0].innerText.toLowerCase();
        const age = row.cells[1].innerText.toLowerCase();
        const pos = row.cells[4].innerText;
        const tradeCell = row.cells[6].innerText;
        let show = true;
        if (search && !(name.includes(search) || age.includes(search) || pos.toLowerCase().includes(search))) {
            show = false;
        }
        if (position && pos !== position) {
            show = false;
        }
        if (tradeStatus === "1" && tradeCell.includes("Not Trade Listed")) {
            show = false;
        }
        if (tradeStatus === "0" && !tradeCell.includes("Not Trade Listed")) {
            show = false;
        }
        row.style.display = show ? '' : 'none';
    });
}