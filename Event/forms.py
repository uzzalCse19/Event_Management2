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


from django import forms
from .models import BlogPost
from django.core.exceptions import ValidationError

from django import forms
from django.core.exceptions import ValidationError
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'cover', 'excerpt', 'body', 'category', 'published']
        widgets = {
            'published': forms.DateInput(attrs={'type': 'date'}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add maxlength attribute to category field (HTML validation)
        self.fields['category'].widget.attrs.update({'maxlength': '50'})

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if len(category) > 50:
            raise ValidationError(
                "Category cannot exceed 50 characters. " 
                f"Current length: {len(category)}"
            )
        return category

    def clean_slug(self):
        return self.instance.slug  # Preserve existing slug during updates

from django import forms
from .models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

 # forms.py
from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }       

 # forms.py
from django import forms
from .models import NewsletterSubscriber

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your email address',
                'class': 'flex-grow px-4 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-white'
            })
        }       