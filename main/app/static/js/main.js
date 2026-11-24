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

                                const left = document.createElement('span');
                                const strong = document.createElement('strong');
                                strong.textContent = hall.studio;
                                left.appendChild(strong);
                                left.appendChild(document.createTextNode(' — ' + hall.name));

                                const right = document.createElement('span');
                                right.textContent = hall.price + ' ₽/ч';

                                div.appendChild(left);
                                div.appendChild(right);
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
            const timeEndInput = this.querySelector('input[name="time_end"]');

            const showError = (input, text) => {
                const error = document.createElement('div');
                error.className = 'form-error js-error';
                input.parentNode.appendChild(error);
                error.textContent = text;
                input.style.borderColor = '#C62828';
            };

            if (nameInput && nameInput.value.trim().length < 2) {
                showError(nameInput, 'Имя должно быть не менее 2 символов');
                hasErrors = true;
            }

            if (phoneInput) {
                const digits = phoneInput.value.replace(/\D/g, '');
                if (digits.length < 9 || digits.length > 15) {
                    showError(phoneInput, 'Введите корректный номер телефона');
                    hasErrors = true;
                }
            }

            if (dateInput && dateInput.value) {
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const selected = new Date(dateInput.value + 'T00:00:00');
                if (selected < today) {
                    showError(dateInput, 'Нельзя забронировать зал на прошедшее время');
                    hasErrors = true;
                }
            }

            if (timeInput && timeEndInput && timeInput.value && timeEndInput.value) {
                if (timeEndInput.value <= timeInput.value) {
                    showError(timeEndInput, 'Время окончания должно быть позже времени начала');
                    hasErrors = true;
                }
            }

            if (hasErrors) {
                e.preventDefault();
            }
        });
    }
});
