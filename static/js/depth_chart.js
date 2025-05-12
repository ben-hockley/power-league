const dropdowns = [
      { listId: 'qbList', headerId: 'qbHeader', inputId: 'qbInput' },
      { listId: 'rbList', headerId: 'rbHeader', inputId: 'rbInput' },
      { listId: 'wrList', headerId: 'wrHeader', inputId: 'wrInput' },
      { listId: 'olList', headerId: 'olHeader', inputId: 'olInput' }
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

    function handleSubmit(e) {
      e.preventDefault();
      dropdowns.forEach(({ listId, inputId }) => {
        const list = document.getElementById(listId);
        const input = document.getElementById(inputId);
        const order = [...list.querySelectorAll('li')].map(li => li.dataset.id);
        input.value = order.join(',');
      });

      alert('Form submitted!\n' +
        dropdowns.map(({ inputId }) => {
          const input = document.getElementById(inputId);
          return `${input.name}: ${input.value}`;
        }).join('\n'));
    }