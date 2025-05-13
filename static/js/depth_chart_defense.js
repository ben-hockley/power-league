document.addEventListener('DOMContentLoaded', () => {
    highlightStarters(); // Run the function when the page loads
    updateLineup(); // Run the function when the page loads
    updateListener(); // Run the function when the page loads
});

const dropdowns = [
      { listId: 'dlList', headerId: 'dlHeader', inputId: 'dl_order' },
      { listId: 'lbList', headerId: 'lbHeader', inputId: 'lb_order' },
      { listId: 'dbList', headerId: 'dbHeader', inputId: 'db_order' },
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
        dlList: 4, // Top 4 DL
        lbList: 3, // Top 3 LBs
        dbList: 4, // Top 4 DBs
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
    const dlList = document.getElementById('dlList');
    const lbList = document.getElementById('lbList');
    const dbList = document.getElementById('dbList');
    const dl1 = dlList.querySelector('li:nth-child(1)');
    const dl2 = dlList.querySelector('li:nth-child(2)');
    const dl3 = dlList.querySelector('li:nth-child(3)');
    const dl4 = dlList.querySelector('li:nth-child(4)');
    const lb1 = lbList.querySelector('li:nth-child(1)');
    const lb2 = lbList.querySelector('li:nth-child(2)');
    const lb3 = lbList.querySelector('li:nth-child(3)');
    const db1 = dbList.querySelector('li:nth-child(1)');
    const db2 = dbList.querySelector('li:nth-child(2)');
    const db3 = dbList.querySelector('li:nth-child(3)');
    const db4 = dbList.querySelector('li:nth-child(4)');

    const lineup = document.getElementById('lineup');
    const playerPositions = [dl1, dl2, dl3, dl4, lb1, lb2, lb3, db1, db2, db3, db4];
    const playerCards = lineup.querySelectorAll('.player-card');
    for (let i = 0; i < playerCards.length; i++) {
        const playerCard = playerCards[i];
        const player = playerPositions[i];
        playerCard.querySelector('.player-name').textContent = player.textContent;
        playerCard.querySelector('.player-rating').textContent = player.getAttribute('skill');
    }
}