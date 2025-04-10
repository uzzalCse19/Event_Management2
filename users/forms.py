from django.contrib.auth.models import User,Group,Permission
from Event.forms import StyledFormMixin
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)


class CustomRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'confirm_password']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email  
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("confirm_password")
        if password1 and confirm_password and password1 != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    


class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a Role",
        label="Assign Role",
        widget=forms.Select(attrs={'class': 'border p-2 rounded'})
    )



class CreateGroupForm(StyledFormMixin,forms.ModelForm):
    permissions=forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permission'
    )
    class Meta:
        model=Group
        fields=['name','permissions']

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })
        }