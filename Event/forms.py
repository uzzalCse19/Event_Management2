from django import forms
from .models import Event, Category
from django.contrib.auth import get_user_model


User=get_user_model()
class StyledFormMixin:
    def add_common_attrs(self, field):
        field.widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring focus:ring-blue-300'
        })
        return field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            self.add_common_attrs(field)

class EventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category', 'participants','asset']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

from django.contrib.auth.forms import UserCreationForm
class UserCreateForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ParticipantForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "w-full px-4 py-2 border rounded-lg"})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg"})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded-lg"})
    )
    events = forms.ModelMultipleChoiceField(
        queryset=Event.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'events']

    def clean_email(self):
        """Ensure the email is unique"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email.")
        return email

    def save(self, commit=True):
        """Save user and assign selected events"""
        user = super().save(commit=False)
        if commit:
            user.save()
            self.cleaned_data['events'].set(user.rsvp_events.all())  # Associate events with the user
        return user



class ParticipantUpdateForm(forms.ModelForm):
    events = forms.ModelMultipleChoiceField(
        queryset=Event.objects.all(),  
        widget=forms.CheckboxSelectMultiple,  
        required=False
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'events']

