from django.db import models
from django.conf import settings
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(Category, related_name='events', on_delete=models.CASCADE)
    asset = models.ImageField(upload_to='event_asset', blank=True, null=True, default="event_asset/default_img.jpg")
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='EventRSVP', 
        related_name='events_attending',
        blank=True
    )
   
    def __str__(self):
        return f"{self.name} ({self.date})"
    


class EventRSVP(models.Model):
    STATUS_CHOICES = [
        ('going', 'Going'),
        ('not_going', 'Not Going'),
        ('maybe', 'Maybe'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='going')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # Prevents duplicate RSVPs

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.status})"
    

