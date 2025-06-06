function confirmDelete(teamId, teamName) {
    document.getElementById('teamNameToDelete').textContent = teamName;
    document.getElementById('teamIdToDelete').value = teamId;
    document.getElementById('deleteTeamForm').action = `/delete_team/${teamId}`;
    var modal = new bootstrap.Modal(document.getElementById('deleteTeamModal'));
    modal.show();
  }