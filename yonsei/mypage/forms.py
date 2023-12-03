from django import forms
from django.contrib.auth.hashers import make_password
from .models import User

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={'class': 'signup-inputs'}),
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={'class': 'signup-inputs'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('비밀번호와 비밀번호 확인이 일치하지 않습니다.')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
