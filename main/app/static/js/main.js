document.addEventListener('DOMContentLoaded', () => {
    const burger = document.getElementById('burger-menu');
    const nav = document.getElementById('nav-menu');

    if (burger && nav) {
        burger.addEventListener('click', () => {
            nav.classList.toggle('active');
        });
    }

    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let timeout = null;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
                return;
            }

            searchResults.innerHTML = '<div style="padding: 12px; color: #666;">Загрузка...</div>';
            searchResults.classList.add('active');

            timeout = setTimeout(() => {
                fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        searchResults.innerHTML = '';
                        if (data.results.length === 0) {
                            searchResults.innerHTML = '<div style="padding: 12px; color: #666;">Ничего не найдено</div>';
                        } else {
                            data.results.forEach(hall => {
                                const div = document.createElement('div');
                                div.className = 'search-result-item';
                                div.innerHTML = `<span><strong>${hall.studio}</strong> — ${hall.name}</span> <span>${hall.price} ₽/ч</span>`;
                                div.addEventListener('click', () => window.location.href = hall.url);
                                searchResults.appendChild(div);
                            });
                        }
                    })
                    .catch(err => {
                        console.error('Ошибка поиска:', err);
                        searchResults.innerHTML = '<div style="padding: 12px; color: red;">Ошибка при поиске</div>';
                    });
            }, 300);
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('active');
            }
        });
    }

    const bookingForm = document.querySelector('.form-card form');

    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            let hasErrors = false;
            

            bookingForm.querySelectorAll('.js-error').forEach(el => el.remove());
            
            const nameInput = this.querySelector('input[name="name"]');
            const phoneInput = this.querySelector('input[name="phone"]');
            const dateInput = this.querySelector('input[name="date"]');
            const timeInput = this.querySelector('input[name="time"]');

            if (nameInput.value.trim().length < 2) {
                showError(nameInput, 'Имя должно быть не менее 2 символов');
                hasErrors = true;
            }

            const phoneRegex = /^\+?[0-9\s\-\(\)]{10,18}$/;
            if (!phoneRegex.test(phoneInput.value)) {
                showError(phoneInput, 'Введите корректный номер телефона');
                hasErrors = true;
            }

            if (!dateInput.value) {
                showError(dateInput, 'Выберите дату');
                hasErrors = true;
            }
            if (!timeInput.value) {
                showError(timeInput, 'Выберите время');
                hasErrors = true;
            }

            if (hasErrors) {
                e.preventDefault();
            }
        });

        function showError(input, message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error js-error';
            errorDiv.style.color = 'red';
            errorDiv.style.fontSize = '14px';
            errorDiv.style.marginTop = '4px';
            errorDiv.textContent = message;
            input.parentNode.appendChild(errorDiv);
            input.style.borderColor = 'red';
        }
    }
});