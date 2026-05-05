from django import forms
from .models import User, cars

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

class loginform(forms.Form):  
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)  

class CarForm(forms.ModelForm):
    class Meta:
        model = cars
        exclude = ['owner', 'is_approved', 'image']

class updateprofileform(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
       
        fields = ['first_name', 'last_name',  'phone_number','profile_picture']

class CarPredictionForm(forms.Form):
    year = forms.IntegerField(label='Year of Purchase', min_value=2000, max_value=2024)
    kms_driven = forms.IntegerField(label='Kms Driven')
    max_power = forms.FloatField(label='Max Power (BHP)')

    FUEL_CHOICES = [(0, 'Petrol'), (1, 'Diesel'), (2, 'CNG'), (3, 'LPG'), (4, 'Electric')]
    SELLER_CHOICES = [(0, 'Individual'), (1, 'Dealer'), (2, 'Trustmark Dealer')]
    TRANSMISSION_CHOICES = [(0, 'Manual'), (1, 'Automatic')]

    fuel_type = forms.ChoiceField(choices=FUEL_CHOICES)
    seller_type = forms.ChoiceField(choices=SELLER_CHOICES)
    transmission = forms.ChoiceField(choices=TRANSMISSION_CHOICES)