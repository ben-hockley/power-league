// Filter the players based on the selected team and enable/disable requested player fields
  function filterPlayers() {
    const selectedTeamId = document.getElementById('other_team_id').value;
    for (let i = 1; i <= 3; i++) {
      const requestSelect = document.getElementById('request_player_' + i);
      if (!requestSelect) continue;
      // Enable or disable the select based on team selection
      requestSelect.disabled = !selectedTeamId;
      Array.from(requestSelect.options).forEach(option => {
        if (option.value === "") return;
        if (option.getAttribute('team_id') !== selectedTeamId && selectedTeamId !== "") {
          option.style.display = 'none';
        } else {
          option.style.display = 'block';
        }
      });
      // Reset selection if not in filtered team
      if (requestSelect.selectedIndex > 0 && requestSelect.options[requestSelect.selectedIndex].style.display === 'none') {
        requestSelect.selectedIndex = 0;
        showPlayerCard('request', i);
      }
      // Hide card if disabled
      if (requestSelect.disabled) {
        document.getElementById('request_card_' + i).style.display = "none";
        requestSelect.setAttribute('title', 'You must select a team to trade with first');
      } else {
        requestSelect.removeAttribute('title');
      }
      // If no team is selected, reset the select to default
      if (!selectedTeamId) {
        requestSelect.selectedIndex = 0;
        showPlayerCard('request', i);
      }
    }
    // Update hidden input when team selection changes
    updateHiddenInputs();
  }

  // Show player card for selected player
  function showPlayerCard(type, idx) {
    const select = document.getElementById(type + '_player_' + idx);
    const card = document.getElementById(type + '_card_' + idx);
    if (!select || !card) return;
    const selected = select.options[select.selectedIndex];
    if (selected && selected.value && !select.disabled) {
      const avatar = selected.getAttribute('data-avatar');
      const name = selected.getAttribute('data-name');
      const position = selected.getAttribute('data-position');
      const age = selected.getAttribute('data-age');
      const skill = selected.getAttribute('data-skill');
      const isTradeListed = selected.getAttribute('data-name').includes('(Trade Listed)');
      card.innerHTML = `
        <div class="card p-2 d-flex flex-row align-items-center" style="width: 100%; min-height:48px;">
          <img src="${avatar}" alt="Avatar" style="width:48px;height:48px;border-radius:8px;border:1px solid #007bff;background:#fff;flex-shrink:0;">
          <div class="ms-3 text-start">
            <div class="fw-bold">${name}${isTradeListed ? ' <span class="badge bg-success text-white ms-1">Trade Listed</span>' : ''}</div>
            <div class="small text-muted">${position} | Age: ${age} | Skill: ${skill}</div>
          </div>
        </div>
      `;
      card.style.display = "block";
    } else {
      card.style.display = "none";
      card.innerHTML = "";
    }
  }

  // Enable/disable submit button based on hidden input values
  function validateTradeForm() {
    const offered = document.getElementById('offered_players').value;
    const requested = document.getElementById('requested_players').value;
    const submitBtn = document.getElementById('submitTradeBtn');
    const warning = document.getElementById('trade-warning');
    if (offered && requested) {
      submitBtn.disabled = false;
      submitBtn.removeAttribute('title');
      warning.style.display = "none";
    } else {
      submitBtn.disabled = true;
      submitBtn.title = "You must offer and request at least one player";
      warning.style.display = "block";
    }
  }

  // Update hidden input fields with comma-separated player IDs
  function updateHiddenInputs() {
    let offered = [];
    let requested = [];
    for (let i = 1; i <= 3; i++) {
      const offerSel = document.getElementById('offer_player_' + i);
      if (offerSel && offerSel.value) {
        offered.push(offerSel.value);
      }
      const requestSel = document.getElementById('request_player_' + i);
      if (requestSel && requestSel.value) {
        requested.push(requestSel.value);
      }
    }
    document.getElementById('offered_players').value = offered.join(',');
    document.getElementById('requested_players').value = requested.join(',');
    validateTradeForm();
  }

  // Initialize player cards and hidden inputs on page load
  document.addEventListener("DOMContentLoaded", function() {
    filterPlayers();
    for (let i = 1; i <= 3; i++) {
      showPlayerCard('offer', i);
      showPlayerCard('request', i);
      // Add change listeners for updating hidden inputs
      const offerSel = document.getElementById('offer_player_' + i);
      if (offerSel) offerSel.addEventListener('change', updateHiddenInputs);
      const requestSel = document.getElementById('request_player_' + i);
      if (requestSel) requestSel.addEventListener('change', updateHiddenInputs);
    }
    // Also update hidden inputs when team selection changes
    const teamSelect = document.getElementById('other_team_id');
    if (teamSelect) teamSelect.addEventListener('change', updateHiddenInputs);
    updateHiddenInputs();
  });