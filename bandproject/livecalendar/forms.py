from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser
from django import forms

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','screenname', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class']='form-control'

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('screenname','userimage', 'username', 'email', 'favorite_band')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['screenname'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['userimage'].widget.attrs['class'] = 'form-control-file'
