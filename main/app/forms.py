from django import forms
from django.core.validators import RegexValidator

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
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Введите телефон в формате +7 900 000-00-00")],
        error_messages={'required': 'Введите номер телефона.'}
    )