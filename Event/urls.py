from django.urls import path
from . import views
from Event.views import rsvp_event,user_profile,dashboard


urlpatterns = [
    path('event_list/',views.event_list,name='event_list'),
    path('event_detail/<int:pk>/',views.event_detail,name='event_detail'),
    path('event/create/',views.create_event,name='create_event'),
    path('event/<int:pk>/update/', views.update_event, name='update_event'),
    path('events/<int:event_id>/delete/',views.delete_event, name='delete_event'),
    path('events/<int:event_id>/confirm-delete/',views.confirm_delete_event, name='confirm_delete_event'),
    path('event/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('organizer_dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('participant/dashboard/',views.participant_dashboard,name='participant_dashboard'),
    path('search/',views.search_events,name='search_events'),
    path('categories/',views.category_list,name='category_list'),
    path('category/create/',views.create_category,name='create_category'),
    path('categories/<int:pk>/update/', views.update_category, name='update_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('participants/',views.participant_list,name='participant_list'),
    path('participants/create/',views.create_participant,name='create_participant'),
    path('participants/<int:pk>/update/',views.update_participant,name='update_participant'),
    path('participants/<int:pk>/delete/',views.delete_participant,name='delete_participant'),
    path('profile/', user_profile, name='profile'),
    path('dashboard/',dashboard,name='dashboard'),

]

