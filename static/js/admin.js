document.getElementById('simulateBtn').addEventListener('click', function() {
    const home = document.getElementById('homeTeam').value;
    const away = document.getElementById('awayTeam').value;
    if (home && away && home !== away) {
        window.location.href = `/match_report/${home}/${away}`;
    } else {
        alert('Please select two different teams.');
    }
});

document.getElementById('ageLeagueBtn').addEventListener('click', function() {
    const leagueId = document.getElementById('leagueSelect').value;
    if (leagueId) {
        window.location.href = `/age_league_players/${leagueId}`;
    } else {
        alert('Please select a league.');
    }
});

document.getElementById('wipeLeagueBtn').addEventListener('click', function() {
    const leagueId = document.getElementById('wipeLeagueSelect').value;
    if (leagueId) {
        window.location.href = `/wipe_league_records/${leagueId}`;
    } else {
        alert('Please select a league.');
    }
});

document.getElementById('generateScheduleBtn').addEventListener('click', function() {
    const leagueId = document.getElementById('scheduleLeagueSelect').value;
    if (leagueId) {
        window.location.href = `/generate_schedule/${leagueId}`;
    } else {
        alert('Please select a league.');
    }
});

document.getElementById('generateDraftBtn').addEventListener('click', function() {
    const leagueId = document.getElementById('draftLeagueSelect').value;
    if (leagueId) {
        window.location.href = `/create_draft_class/${leagueId}`;
    } else {
        alert('Please select a league.');
    }
});

document.getElementById('newSeasonBtn').addEventListener('click', function() {
    const leagueId = document.getElementById('newSeasonLeagueSelect').value;
    if (leagueId) {
        window.location.href = `/new_season/${leagueId}`;
    } else {
        alert('Please select a league.');
    }
});