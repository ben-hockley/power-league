document.addEventListener('DOMContentLoaded', () => {
    highlightStarters(); // Run the function when the page loads
    updateLineup(); // Run the function when the page loads
    updateListener(); // Run the function when the page loads
});

const dropdowns = [
      { listId: 'qbList', headerId: 'qbHeader', inputId: 'qb_order' },
      { listId: 'rbList', headerId: 'rbHeader', inputId: 'rb_order' },
      { listId: 'wrList', headerId: 'wrHeader', inputId: 'wr_order' },
      { listId: 'olList', headerId: 'olHeader', inputId: 'ol_order' }
    ];

    dropdowns.forEach(({ listId, headerId }) => updateHeader(listId, headerId));

    dropdowns.forEach(({ listId, headerId }) => {
      const list = document.getElementById(listId);
      const header = document.getElementById(headerId);
      let draggingEl;

      list.addEventListener('dragstart', (e) => {
        draggingEl = e.target;
        e.target.classList.add('dragging');
      });

      list.addEventListener('dragend', (e) => {
        e.target.classList.remove('dragging');
        updateHeader(listId, headerId);
        highlightStarters();
        updateLineup();
        updateListener();
      });

      list.addEventListener('dragover', (e) => {
        e.preventDefault();
        const afterElement = getDragAfterElement(list, e.clientY);
        if (!afterElement) {
          list.appendChild(draggingEl);
        } else {
          list.insertBefore(draggingEl, afterElement);
        }
      });
    });

    function updateHeader(listId, headerId) {
      const list = document.getElementById(listId);
      const header = document.getElementById(headerId);
      const firstItem = list.querySelector('li');
      if (firstItem) {
        header.textContent = firstItem.textContent;
      }
    }

    function getDragAfterElement(container, y) {
      const draggableElements = [...container.querySelectorAll('li:not(.dragging)')];
      return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
          return { offset, element: child };
        } else {
          return closest;
        }
      }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    function updateListener() {
      dropdowns.forEach(({ listId, inputId }) => {
        const list = document.getElementById(listId);
        const input = document.getElementById(inputId);
        const order = [...list.querySelectorAll('li')].map(li => li.dataset.id);
        input.value = JSON.stringify(order).slice(1, -1).replaceAll(/"/g, '');
      });
    }

function highlightStarters() {
    const lists = {
        qbList: 1, // Top 1 QB
        rbList: 2, // Top 2 RBs
        wrList: 3, // Top 3 WRs
        olList: 5  // Top 5 OLs
    };

    Object.entries(lists).forEach(([listId, count]) => {
        const list = document.getElementById(listId);
        const items = list.querySelectorAll('li');

        items.forEach((item, index) => {
            if (index < count) {
                item.style.color = 'blue'; // Apply blue color to the top items
                item.style.fontWeight = 'bold'; // Optional: Make them bold
            } else {
                item.style.color = ''; // Reset color for other items
                item.style.fontWeight = ''; // Reset font weight for other items
            }
        });
    });
}

function updateLineup() {
    const qbList = document.getElementById('qbList');
    const rbList = document.getElementById('rbList');
    const wrList = document.getElementById('wrList');
    const olList = document.getElementById('olList');
    const qb = qbList.querySelector('li');
    const rb1 = rbList.querySelector('li:nth-child(1)');
    const rb2 = rbList.querySelector('li:nth-child(2)');
    const wr1 = wrList.querySelector('li:nth-child(1)');
    const wr2 = wrList.querySelector('li:nth-child(2)');
    const wr3 = wrList.querySelector('li:nth-child(3)');
    const ol1 = olList.querySelector('li:nth-child(1)');
    const ol2 = olList.querySelector('li:nth-child(2)');
    const ol3 = olList.querySelector('li:nth-child(3)');
    const ol4 = olList.querySelector('li:nth-child(4)');
    const ol5 = olList.querySelector('li:nth-child(5)');

    const lineup = document.getElementById('lineup');
    const playerPositions = [qb, rb1, rb2, wr1, wr2, wr3, ol1, ol2, ol3, ol4, ol5];
    const playerCards = lineup.querySelectorAll('.player-card');
    for (let i = 0; i < playerCards.length; i++) {
        const playerCard = playerCards[i];
        const player = playerPositions[i];
        playerCard.querySelector('.player-name').textContent = player.textContent;
        playerCard.querySelector('.player-rating').textContent = player.getAttribute('skill');
        // Display SVG avatar
        playerCard.querySelector('.player-avatar').setAttribute('src', '/static/avatars/' + player.getAttribute('data-id') + '.svg');
        playerCard.querySelector('.player-avatar').setAttribute('alt', player.textContent);
    }
}