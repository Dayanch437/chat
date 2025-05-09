from django import forms
from .models import Account

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email',"phone_number", 'password']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {'placeholder': 'First Name',type:'text'}
        self.fields['last_name'].widget.attrs = {'placeholder': 'Last Name',type:'text'}
        self.fields['email'].widget.attrs = {'placeholder': 'Email',type:'email'}
        self.fields['phone_number'].widget.attrs = {'placeholder': 'Phone Number',type:'tel'}
        self.fields['password'].widget.attrs = {'placeholder': 'Password',type:'password'}
        self.fields['confirm_password'].widget.attrs = {'placeholder': 'confirm password',type:'password'}
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords must match")


