function toggleLeagueCodeField() {
    const isPublic = document.getElementById('is_public').checked;
    document.getElementById('leagueCodeGroup').style.display = isPublic ? 'none' : 'block';
    if (isPublic) {
      document.getElementById('league_code').value = '';
    }
  }
  function generateLeagueCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 10; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    document.getElementById('league_code').value = code;
  }
  // Ensure correct display on page load
  document.addEventListener('DOMContentLoaded', toggleLeagueCodeField);