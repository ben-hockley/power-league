  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('toggleLeagueCodeBtn');
    const code = document.getElementById('hiddenLeagueCode');
    if (btn) {
      btn.addEventListener('click', function() {
        if (code.style.display === 'none') {
          code.style.display = 'inline';
          btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
        } else {
          code.style.display = 'none';
          btn.innerHTML = '<i class="bi bi-eye"></i>';
        }
      });
    }
  });