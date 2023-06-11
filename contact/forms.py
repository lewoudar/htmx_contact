from django import forms


class ContactForm(forms.Form):
    firstname = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'first name'}))
    lastname = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'last name'}))
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'email'}))
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'phone'}))
