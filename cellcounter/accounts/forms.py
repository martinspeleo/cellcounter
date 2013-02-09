from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm, UserChangeForm

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class EmailChangeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("email",)


class UserNameReminderForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if len(User.objects.filter(email = email)) == 0:
            raise forms.ValidationError("Unregistered E-mail address.")
        return email


class RequestPasswordResetForm(forms.Form):
    username = forms.CharField(required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(User.objects.filter(username = username)) == 0:
            raise forms.ValidationError("Unregistered username.")
        return username

