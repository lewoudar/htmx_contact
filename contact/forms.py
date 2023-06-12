from django import forms
from django.core.exceptions import ValidationError

from .models import Contact


class ContactForm(forms.Form):
    firstname = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'first name'}))
    lastname = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'last name'}))
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'email'}))
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'phone'}))

    def clean_email(self) -> str | None:
        email = self.cleaned_data.get('email')
        if email is not None and Contact.objects.filter(email=email).exists():
            raise ValidationError(f'Email {email} already exists')
        return email
