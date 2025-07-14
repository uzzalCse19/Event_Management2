from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q,Case,When,IntegerField,Prefetch
from .models import Event, Category,EventRSVP
from django.contrib.auth.models import Group
from .forms import EventForm,CategoryForm,ParticipantForm 
from django.utils import timezone
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.contrib import messages
from users.views import is_admin
from django.db import models 
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .forms import ParticipantUpdateForm
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView,CreateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import get_user_model
from users.views import is_admin
from django.utils import timezone
from datetime import datetime, timedelta
import calendar

# Add this at the top of views.py
from django.utils.text import slugify

# Then in BlogPostCreateView
def form_valid(self, form):
    # Ensure unique slug
    slug = slugify(form.instance.title)
    unique_slug = slug
    num = 1
    while BlogPost.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{slug}-{num}'
        num += 1
    form.instance.slug = unique_slug
    return super().form_valid(form)

User=get_user_model()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()



# def home(request):
#     upcoming_events = Event.objects.filter(
#         date__gte=timezone.now().date()
#     ).order_by('date', 'time')[:5]  
    
   
#     if request.user.is_authenticated:
#         user_rsvps = EventRSVP.objects.filter(
#             user=request.user,
#             event__date__gte=timezone.now().date()
#         ).select_related('event').order_by('event__date')[:3]
#     else:
#         user_rsvps = [] 
    
    
#     recent_events = Event.objects.order_by('-id')[:3]
#     context = {
#         'upcoming_events': upcoming_events,
#         'user_rsvps': user_rsvps,
#         'recent_events': recent_events,
#     }
#     return render(request, 'home.html', context)


# def event_list(request):
#     events=Event.objects.select_related('category').prefetch_related('participants').all()
#     if request.user.is_authenticated:
#         for event in events:
#             event.user_has_resvp=request.user in event.participants.all()
#     return render(request,'event_list.html',{'events':events})


class EventListView(ListView):
    model=Event
    template_name='event_list.html'
    context_object_name='events'

    def get_queryset(self):
        return Event.objects.select_related('category').prefetch_related('participants')
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        events=context['events']
        user=self.request.user

        if user.is_authenticated:
            for event in events:
                event.user_has_rsvp=user in event.participants.all()
        return context
    


    

def event_detail(request,pk):
    event=get_object_or_404(Event,pk=pk)
    return render(request,'event_detail.html',{'event':event})


@login_required
def rsvp_event(request,event_id):
    event=get_object_or_404(Event,pk=event_id)
    if EventRSVP.objects.filter(event=event,user=request.user).exists():
        messages.warning(request,"You've already this event!")
    else:
        EventRSVP.objects.create(event=event,user=request.user)
        messages.success(request,"Successfully reserved the event")
    return redirect('event_list')




@login_required
@permission_required("Event.add_event", login_url='no-permission')
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST,request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            if request.user.is_authenticated:
                event.participants.add(request.user, through_defaults={'status': 'going'})
            
            messages.success(request, 'Event created successfully!')
            return redirect('event_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm(initial={
            'date': timezone.now().date(),
            'time': timezone.now().time()
        })
    categories = Category.objects.all()
    return render(request, 'event_form.html', {
        'form': form,
        'categories': categories
    })




class EventUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    context_object_name = 'event'
    permission_required = 'Event.change_event' 
    login_url = 'no-permission'
      
    def get_success_url(self):
        return reverse_lazy('event_list')
    def form_valid(self, form):
        updated_event = form.save()
        messages.success(self.request, f'Event "{updated_event.name}" has been updated successfully!')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['is_update'] = True
        return context
    

@login_required
@permission_required("Event.change_event", login_url='no-permission')
def confirm_delete_event(request,event_id):
    event=get_object_or_404(Event,id=event_id)
    return render(request,'event_confirm_delete.html',{'event':event})



# @login_required
# @permission_required("Event.change_event", login_url='no-permission')
# def delete_event(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     if not request.user.groups.filter(name__in=['Organizer', 'Admin']).exists():
#         messages.error(request, "You don't have permission to delete events.")
#         return redirect('event_detail', event_id=event.id)
#     if request.method == 'POST':
#         event_name = event.name
#         event.delete()
#         messages.success(request, f"Event '{event_name}'deleted successfully.")
#         return redirect('event_list')
#     return redirect('event_detail', event_id=event.id)
class EventDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'Event.change_event'
    login_url = 'no-permission'

    def post(self, request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        if not request.user.groups.filter(name__in=['Organizer', 'Admin']).exists():
             messages.error(request, "You don't have permission to delete events.")
             return redirect('event_detail', event_id=event.id)
        event_name = event.name
        event.delete()
        messages.success(request, f"Event '{event_name}' deleted successfully.")
        return redirect('event_list')
    
    def get(self, request, event_id, *args, **kwargs):
        return redirect('event_detail', event_id=event_id)

  
@user_passes_test(is_organizer, login_url='no-permission') 
def organizer_dashboard(request):
    events=Event.objects.all()
    categories=Category.objects.all()
    return render(request, 'organizer_dashboard.html', {
        'events':events,
        'categories':categories
    })


def participant_dashboard(request):
    rsvps = EventRSVP.objects.filter(user=request.user).select_related('event')
    return render(request, 'participant_dashboard.html', {
        'rsvps': rsvps
    })



def search_events(request):
    query = request.GET.get('q', '')
    events = Event.objects.filter(
        Q(name__icontains=query) | 
        Q(location__icontains=query) |
        Q(category__name__icontains=query)
        ) if query else Event.objects.all()
    return render(request, 'event_list.html', {'events': events, 'query': query})


@login_required
@permission_required("Event.view_category", login_url='no-permission')
def category_list(request):
    categories=Category.objects.annotate(event_count=Count('events'))
    return render(request,'category_list.html',{'categories':categories})
    
          

class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')
    permission_required = 'Event.add_category'
    login_url = 'no-permission'
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

            
# @login_required
# @permission_required("Event.change_category", login_url='no-permission')         
# def update_category(request, pk): 
#     category = get_object_or_404(Category, pk=pk) 
#     if request.method == 'POST':
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             form.save()
#             return redirect('category_list')
#     else:
#         form = CategoryForm(instance=category)
#     return render(request, 'category_form.html', {'form': form})

class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category_list')
    permission_required = 'Event.change_category'
    login_url = 'no-permission'

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Category

class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    login_url = 'no-permission'
    permission_required = 'events.delete_category'  

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f"Category '{category.name}' has been deleted.")
        return super().delete(request, *args, **kwargs)


    
    


@login_required
@permission_required("auth.view_user", login_url='no-permission')
def participant_list(request):
    rsvp_qs = EventRSVP.objects.filter(status__in=['going', 'maybe'])
    participants = User.objects.prefetch_related(
        Prefetch('eventrsvp_set', queryset=rsvp_qs)
        ).annotate(
            going_count=Count(
                Case(
                    When(eventrsvp__status='going', then=1),
                    output_field=IntegerField()
                )
            ),
            maybe_count=Count(
                Case(
                    When(eventrsvp__status='maybe', then=1),
                    output_field=IntegerField()
                )
            ),
            total_events=Count('eventrsvp')
            ).order_by('-date_joined')
    return render(request, 'participant_list.html', {'participants': participants})
    return render(request, 'participant_list.html', {
        'participants': participants,
        'total_participants': participants.count()
    })


 
@login_required
def create_participant(request): 
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            form.save_m2m()
            participant_group, created = Group.objects.get_or_create(name='Participant')
            user.groups.add(participant_group)
            messages.success(request, "Participant created successfully and added to 'Participant' group!")
            return redirect('participant_list')
    else:
        form = ParticipantForm()
    return render(request, 'participant_form.html', {'form': form})
    

@login_required
@permission_required("auth.change_user", login_url='no-permission')
def update_participant(request, pk):
    participant = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = ParticipantUpdateForm(request.POST, instance=participant)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.save()
            form.save_m2m()
            messages.success(request, "Participant updated successfully!")
            return redirect('participant_list')
    else:
        form = ParticipantUpdateForm(instance=participant)
    return render(request, 'participant_form.html', {'form': form})


class ParticipantDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'participant_confirm_delete.html'
    success_url = reverse_lazy('participant_list')
    context_object_name = 'user'
    permission_required = 'auth.delete_user'
    login_url = 'no-permission'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(request, f"User '{user.username}' deleted successfully!")
        return super().delete(request, *args, **kwargs)



@login_required
def user_profile(request):
    rsvps = EventRSVP.objects.filter(
        user=request.user,
        event__date__gte=timezone.now().date()
    ).select_related('event').order_by('event__date')
    past_rsvps = EventRSVP.objects.filter(
        user=request.user,
        event__date__lt=timezone.now().date()
    ).select_related('event').order_by('-event__date')[:10]  
    context = {
        'user': request.user,
        'upcoming_events': [rsvp.event for rsvp in rsvps],
        'past_events': [rsvp.event for rsvp in past_rsvps],
        'rsvp_statuses': {rsvp.event.id: rsvp.get_status_display() for rsvp in rsvps},
    }
    return render(request, 'profile.html', context)



@login_required
def dashboard(request):
    if is_participant(request.user):
        return redirect('participant_dashboard')
    elif is_organizer(request.user):
        return redirect('organizer_dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')
    return redirect('no-permission')

@receiver(post_save, sender=EventRSVP)
def send_rsvp_email(sender, instance, created, **kwargs):
    if created:
        subject = f"RSVP Confirmation for {instance.event.name}"
        message = f"Hi {instance.user.username},\n\nYou have successfully RSVP'd for the event: {instance.event.name}."
        recipient_list = [instance.user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)




from django.utils import timezone
from django.views.generic import TemplateView
from Event.models import Event, EventRSVP,Offer,BlogPost,Testimonial


from django.views.generic import TemplateView
from django.utils import timezone
from .models import Event, EventRSVP, Offer, BlogPost, Testimonial

from django.views.generic import TemplateView
from django.utils import timezone
from .models import Event, EventRSVP, Offer, BlogPost, Testimonial

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        current_month = today.month
        
        # Generate dynamic upcoming months (current + next 4)
        upcoming_months = []
        for i in range(5):  # Current month + next 4 months
            month_num = (current_month - 1 + i) % 12 + 1
            month_name = calendar.month_name[month_num]
            upcoming_months.append({
                'num': str(month_num),
                'name': month_name[:3]  # Short name (Jun, Jul, etc)
            })
        
        context['current_month'] = current_month
        context['upcoming_months'] = upcoming_months
        
        # Rest of your context data remains the same
        context['upcoming_events'] = Event.objects.filter(
            date__gte=today
        ).order_by('date', 'time')[:8]
        
        context['recent_events'] = Event.objects.order_by('-date')[:4]

        # Marketing content
        context['offers'] = Offer.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )[:3]
        
        context['blog_posts'] = BlogPost.objects.filter(
            published__lte=today
        ).order_by('-published')[:3]
        
        context['testimonials'] = Testimonial.objects.filter(
            is_featured=True
        )[:3]

        # User-specific data
        if self.request.user.is_authenticated:
            context['user_rsvps'] = EventRSVP.objects.filter(
                user=self.request.user,
                event__date__gte=today
            ).select_related('event').order_by('event__date')[:3]
        else:
            context['user_rsvps'] = None

        return context
    

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
from .models import BlogPost
from .forms import BlogPostForm
import uuid
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'


@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog_form.html'
    success_url = reverse_lazy('blog_list')

    def form_valid(self, form):
        # Generate unique slug
        slug = slugify(form.instance.title)
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:4]}"
        form.instance.slug = slug
        return super().form_valid(form)
    
@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog_form.html'
    slug_field = 'slug'

    def get_success_url(self):
        return reverse_lazy('blog_detail', kwargs={'slug': self.object.slug})
    
@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'blog_confirm_delete.html'
    success_url = reverse_lazy('blog_list')
    slug_field = 'slug'


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Offer
from .forms import OfferForm


@login_required
def create_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer created successfully!')
            return redirect('offers_list')
    else:
        form = OfferForm()
    return render(request, 'offer_form.html', {'form': form})

@login_required
def update_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer updated successfully!')
            return redirect('offers_list')
    else:
        form = OfferForm(instance=offer)
    return render(request, 'offer_form.html', {'form': form})

@login_required
def delete_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    if request.method == 'POST':
        offer.delete()
        messages.success(request, 'Offer deleted successfully!')
        return redirect('offers_list')
    return render(request, 'offer_confirm_delete.html', {'offer': offer})

class OfferListView(ListView):
    model = Offer
    template_name = 'offer_list.html'
    context_object_name = 'offers'
    ordering = ['-start_date']
    paginate_by = 10


 # views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Testimonial
from .forms import TestimonialForm



@login_required
def create_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial created successfully!')
            return redirect('testimonials_list')
    else:
        form = TestimonialForm()
    return render(request, 'testimonial_form.html', {'form': form})

@login_required
def update_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated successfully!')
            return redirect('testimonials_list')
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, 'testimonial_form.html', {'form': form})

@login_required
def delete_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully!')
        return redirect('testimonials_list')
    return render(request, 'testimonial_confirm_delete.html', {'testimonial': testimonial})

class TestimonialListView(ListView):
    model = Testimonial
    template_name = 'testimonial_list.html'
    context_object_name = 'testimonials'
    ordering = ['-id']
    paginate_by = 10   

 # views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for subscribing!')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            # If email already exists
            messages.info(request, 'You are already subscribed!')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')   