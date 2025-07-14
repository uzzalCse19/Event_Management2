from django.urls import path
from Event.views import rsvp_event,dashboard,HomeView,EventListView,CategoryDeleteView,event_detail,search_events,participant_list,dashboard,create_event,EventUpdateView,EventDeleteView,confirm_delete_event,rsvp_event,organizer_dashboard,participant_dashboard,category_list,CategoryCreateView,CategoryUpdateView,create_participant,update_participant,ParticipantDeleteView
from django.urls import path
from .views import (
    BlogPostListView,
    BlogPostDetailView,
    BlogPostCreateView,
    BlogPostUpdateView,
    BlogPostDeleteView
)
from .views import create_offer, update_offer, delete_offer, OfferListView
from django.utils.text import slugify
from .views import (create_testimonial, update_testimonial,delete_testimonial, TestimonialListView,newsletter_subscribe)


urlpatterns = [
    # path('event_list/',  event_list,name='event_list'),
    path('event_list/',  EventListView.as_view(),name='event_list'),
    path('event_detail/<int:pk>/',  event_detail,name='event_detail'),
    path('event/create/',  create_event,name='create_event'),
    path('event/<int:pk>/update/',  EventUpdateView.as_view(), name='update_event'),
    path('events/<int:event_id>/delete/', EventDeleteView.as_view(), name='delete_event'),
    path('events/<int:event_id>/confirm-delete/',confirm_delete_event, name='confirm_delete_event'),
    path('event/<int:event_id>/rsvp/',  rsvp_event, name='rsvp_event'),
    path('organizer_dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('participant/dashboard/', participant_dashboard,name='participant_dashboard'),
    path('search/',  search_events,name='search_events'),
    path('categories/',  category_list,name='category_list'),
    path('category/create/',CategoryCreateView.as_view(),name='create_category'),
    path('categories/<int:pk>/update/',CategoryUpdateView.as_view(), name='update_category'),
    path('categories/<int:pk>/delete/',CategoryDeleteView.as_view(), name='delete_category'),
    path('participants/',  participant_list,name='participant_list'),
    path('participants/create/',  create_participant,name='create_participant'),
    path('participants/<int:pk>/update/',  update_participant,name='update_participant'),
    path('participants/<int:pk>/delete/',ParticipantDeleteView.as_view(),name='delete_participant'),
    # path('profile/', user_profile, name='profile'),
    path('dashboard/',dashboard,name='dashboard'),
    # path('home/',home,name="home"),
    path('home/', HomeView.as_view(), name='home'),
    path('blog/', BlogPostListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', BlogPostDetailView.as_view(), name='blog_detail'),
    path('blog/create/', BlogPostCreateView.as_view(), name='blog_create'),
    
    path('blog/<slug:slug>/edit/', BlogPostUpdateView.as_view(), name='blog_update'),
    path('blog/<slug:slug>/delete/', BlogPostDeleteView.as_view(), name='blog_delete'),
    path('offers/', OfferListView.as_view(), name='offers_list'),
    path('offers/create/', create_offer, name='create_offer'),
    path('offers/<int:pk>/update/', update_offer, name='update_offer'),
    path('offers/<int:pk>/delete/', delete_offer, name='delete_offer'),

    path('testimonials/', TestimonialListView.as_view(), name='testimonials_list'),
    path('testimonials/create/', create_testimonial, name='create_testimonial'),
    path('testimonials/<int:pk>/update/', update_testimonial, name='update_testimonial'),
    path('testimonials/<int:pk>/delete/', delete_testimonial, name='delete_testimonial'),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
]





