function confirmDelete(teamId, teamName) {
      document.getElementById('teamNameToDelete').textContent = teamName;
      document.getElementById('confirmDeleteBtn').href = '/delete_team/' + teamId;
      var deleteModal = new bootstrap.Modal(document.getElementById('deleteTeamModal'));
      deleteModal.show();
    }