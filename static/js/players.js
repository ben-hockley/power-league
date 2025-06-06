document.getElementById('player-search').addEventListener('input', filterPlayersTable);
document.getElementById('team-filter').addEventListener('change', filterPlayersTable);
document.getElementById('position-filter').addEventListener('change', filterPlayersTable);
document.getElementById('trade-filter').addEventListener('change', filterPlayersTable);

function filterPlayersTable() {
    const search = document.getElementById('player-search').value.toLowerCase();
    const team = document.getElementById('team-filter').value;
    const position = document.getElementById('position-filter').value;
    const trade = document.getElementById('trade-filter').value;
    document.querySelectorAll('#roster-table tbody tr').forEach(function(row) {
        const name = row.cells[0].innerText.toLowerCase();
        const teamCell = row.cells[6].innerText.trim();
        const pos = row.cells[4].innerText.trim();
        const tradeStatus = row.cells[7].innerText.trim();
        let show = true;
        if (search && !name.includes(search)) show = false;
        if (team && teamCell !== team) show = false;
        if (position && pos !== position) show = false;
        if (trade) {
            if (trade === "1" && !tradeStatus.includes("Yes")) show = false;
            if (trade === "0" && !tradeStatus.includes("No")) show = false;
        }
        row.style.display = show ? '' : 'none';
    });
}