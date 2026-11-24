import re

from datetime import datetime

from django import forms


class BookingForm(forms.Form):
    date = forms.DateField(
        label="Дата съёмки",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        error_messages={'required': 'Пожалуйста, выберите дату.'}
    )
    time = forms.TimeField(
        label="Время начала",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        error_messages={'required': 'Выберите время начала съёмки.'}
    )
    time_end = forms.TimeField(
        label="Время окончания",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        error_messages={'required': 'Выберите время окончания съёмки.'}
    )
    name = forms.CharField(
        label="Ваше имя",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Как к вам обращаться'}),
        error_messages={'required': 'Введите имя.'}
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 900 000-00-00'}),
        error_messages={'required': 'Введите номер телефона.'}
    )

    def clean_phone(self):
        raw = self.cleaned_data.get('phone', '')
        digits = re.sub(r'\D', '', raw or '')
        if len(digits) == 11 and digits[0] in '78':
            return '+7' + digits[1:]
        if len(digits) == 10:
            return '+7' + digits
        raise forms.ValidationError('Введите телефон в формате +7 900 000-00-00 — например, +7 900 123-45-67')

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Имя должно быть не менее 2 символов.')
        return name

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        start = cleaned.get('time')
        end = cleaned.get('time_end')

        if date:
            today = datetime.now().date()
            if date < today:
                raise forms.ValidationError('Нельзя забронировать зал на прошедшее время. Выберите другую дату.')

        if start and end and end <= start:
            raise forms.ValidationError('Время окончания должно быть позже времени начала.')

        return cleaned
