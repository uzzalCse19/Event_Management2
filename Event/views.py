from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from .models import Event, Category,EventRSVP
from django.contrib.auth.models import User,Group
from .forms import EventForm,StyledFormMixin,CategoryForm,ParticipantForm 
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
from django.db.models import Count, Case, When, IntegerField


def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()



def home(request):
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date', 'time')[:5]  
    
   
    if request.user.is_authenticated:
        user_rsvps = EventRSVP.objects.filter(
            user=request.user,
            event__date__gte=timezone.now().date()
        ).select_related('event').order_by('event__date')[:3]
    else:
        user_rsvps = [] 
    
    
    recent_events = Event.objects.order_by('-id')[:3]
    context = {
        'upcoming_events': upcoming_events,
        'user_rsvps': user_rsvps,
        'recent_events': recent_events,
    }
    return render(request, 'home.html', context)


def event_list(request):
    events=Event.objects.select_related('category').prefetch_related('participants').all()
    if request.user.is_authenticated:
        for event in events:
            event.user_has_resvp=request.user in event.participants.all()
    return render(request,'event_list.html',{'events':events})
    

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




@login_required
@permission_required("Event.change_event", login_url='no-permission')
def update_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save()
            messages.success(request, f'Event "{updated_event.name}" has been updated successfully!')
            return redirect('event_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm(instance=event)
    context = {
        'form': form,
        'categories': Category.objects.all(),
        'event': event,  
        'is_update': True  
    }
    return render(request, 'event_form.html', context)


@login_required
@permission_required("Event.change_event", login_url='no-permission')
def confirm_delete_event(request,event_id):
    event=get_object_or_404(Event,id=event_id)
    return render(request,'event_confirm_delete.html',{'event':event})



@login_required
@permission_required("Event.change_event", login_url='no-permission')
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not request.user.groups.filter(name__in=['Organizer', 'Admin']).exists():
        messages.error(request, "You don't have permission to delete events.")
        return redirect('event_detail', event_id=event.id)
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f"Event '{event_name}'deleted successfully.")
        return redirect('event_list')
    return redirect('event_detail', event_id=event.id)


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
    
          
@login_required
@permission_required("Event.add_category", login_url='no-permission')
def create_category(request):
        if request.method == 'POST':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('category_list')
        else:
            form = CategoryForm()
        return render(request, 'category_form.html', {'form': form})


    
        
        
            
@login_required
@permission_required("Event.change_category", login_url='no-permission')         
def update_category(request, pk): 
    category = get_object_or_404(Category, pk=pk) 
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})
   

@login_required
@permission_required("Event.delete_category", login_url='no-permission')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})


@login_required
@permission_required("auth.view_user", login_url='no-permission')
def participant_list(request):
    participants = User.objects.annotate(
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


@login_required
@permission_required("auth.delete_user", login_url='no-permission')
def delete_participant(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('participant_list')
    return render(request, 'participant_confirm_delete.html', {'user': user})



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

