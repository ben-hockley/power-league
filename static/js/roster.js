// Simple table sort for integer columns and custom position order
document.addEventListener("DOMContentLoaded", function() {
    const table = document.getElementById("roster-table");
    const intCols = [1, 2, 3, 5]; // Age, Draft Year, Draft Pick, Skill (0-based)
    const positionCol = 4; // Position column index (0-based)
    const positionOrder = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"];

    function sortTable(table, col, isInt, asc=true, isPosition=false) {
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.querySelectorAll("tr"));
        rows.sort((a, b) => {
            let aText = a.children[col].textContent.trim();
            let bText = b.children[col].textContent.trim();
            if (isPosition) {
                let aIdx = positionOrder.indexOf(aText);
                let bIdx = positionOrder.indexOf(bText);
                aIdx = aIdx === -1 ? 999 : aIdx;
                bIdx = bIdx === -1 ? 999 : bIdx;
                return asc ? aIdx - bIdx : bIdx - aIdx;
            }
            if (isInt) {
                aText = parseInt(aText, 10);
                bText = parseInt(bText, 10);
                if (isNaN(aText)) aText = -Infinity;
                if (isNaN(bText)) bText = -Infinity;
            }
            return asc ? (aText > bText ? 1 : aText < bText ? -1 : 0)
                       : (aText < bText ? 1 : aText > bText ? -1 : 0);
        });
        rows.forEach(row => tbody.appendChild(row));
    }

    let lastSortedCol = -1;
    let lastAsc = true;

    table.querySelectorAll("th").forEach((th, idx) => {
        th.style.cursor = "pointer";
        th.addEventListener("click", function() {
            const isInt = intCols.includes(idx);
            const isPosition = idx === positionCol;
            let asc = true;
            if (lastSortedCol === idx) asc = !lastAsc;
            sortTable(table, idx, isInt, asc, isPosition);
            lastSortedCol = idx;
            lastAsc = asc;
        });
    });
});