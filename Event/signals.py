from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import EventRSVP

@receiver(post_save, sender=EventRSVP)
def send_rsvp_email(sender, instance, created, **kwargs):
    if created:
        # Send an email to the participant
        subject = f"RSVP Confirmation for {instance.event.name}"
        message = f"Hi {instance.user.username},\n\nYou have successfully RSVP'd for the event: {instance.event.name}.\n\nThank You\n\n Event Management Team"
        recipient_list = [instance.user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
