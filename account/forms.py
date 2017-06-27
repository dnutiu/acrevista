from django.contrib.auth.models import User
from django import forms
from .models import Profile


# Form that will allow user to change first and last name.
class ChangeNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


# Form that will allow a profile to be edited.
class EditProfileForm(forms.ModelForm):
    phone = forms.CharField(label="Phone", widget=forms.TextInput, required=False)
    affiliation = forms.CharField(label="Affiliation", widget=forms.TextInput, required=False)
    country = forms.ChoiceField(label="Country", widget=forms.Select, choices=Profile.COUNTRY_CHOICES, required=False)
    title = forms.ChoiceField(label="Title", widget=forms.Select, choices=Profile.TITLE_CHOICES, required=False)

    class Meta:
        model = Profile
        fields = ('title', 'phone', 'country', 'affiliation')


# This form will change email for the user.
class ChangeEmailForm(forms.ModelForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput, required=True)
    email = forms.EmailField(label="Email", widget=forms.EmailInput, required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        return self.cleaned_data['username']


# This form will login the user.
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# This form will register the user.
class UserRegistrationForm(forms.ModelForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput, required=True, max_length=64)
    first_name = forms.CharField(label="First Name", widget=forms.TextInput, required=True)
    last_name = forms.CharField(label="Last Name", widget=forms.TextInput, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput, required=True)
    email = forms.EmailField(label="Email", widget=forms.EmailInput, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    # Set email as username, username must be an email.
    def clean_email(self):
        return self.cleaned_data['username']

    # Also take a look at UserCreationForm from django.contrib.auth.forms
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
