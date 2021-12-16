from django import forms
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()

class LoginForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Логин"
        self.fields['password'].label = "Пароль"

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError(f'Пользователь с логином {username} не найден')
        if not user.check_password(password):
            raise forms.ValidationError(f"Пароль неверный")
        return self.cleaned_data




class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Логин"
        self.fields['password'].label = "Пароль"
        self.fields['confirm_password'].label = "Подтвердите пароль"
        self.fields['email'].label = "Почта"

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Почта уже занята")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Логин уже занят")
        return username

    def clean(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
        return self.cleaned_data


    class Meta:
        model = User
        fields = ['username','email', 'password', 'confirm_password']


class OrderForm(forms.ModelForm):

    email = forms.EmailField(widget=forms.TextInput(attrs={"type":"email"}))

    class Meta:
        model = Order
        fields = ('email',)