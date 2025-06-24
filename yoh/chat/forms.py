from django import forms 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1','password2']

class LoginForm(AuthenticationForm):
    pass

class AddFriendForm(forms.Form):
    friend_id = forms.IntegerField(label="Friend's User ID")

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)