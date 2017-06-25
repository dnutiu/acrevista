from django.contrib.auth.models import User
from django import forms


# This form will login the user.
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# This form will register the user.
class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name", widget=forms.TextInput, required=True)
    last_name = forms.CharField(label="Last Name", widget=forms.TextInput, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput, required=True)
    email = forms.EmailField(label="Email", widget=forms.EmailInput, required=True)
    bio = forms.CharField(label="Bio", widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    # Not sure if needed anymore...
    # def clean_last_name(self):
    #     cd = self.cleaned_data
    #     if not cd['last_name']:
    #         raise forms.ValidationError('Last Name is required.')
    #     return cd['last_name']
    #
    # def clean_first_name(self):
    #     cd = self.cleaned_data
    #     if not cd['first_name']:
    #         raise forms.ValidationError('First Name is required.')
    #     return cd['first_name']

    # Also take a look at UserCreationForm from django.contrib.auth.forms
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
