from django.db import models
from django.conf import settings
from django.utils import timezone

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
    


# core/models.py  (or a new app “marketing”, etc.)

class Offer(models.Model):
    title         = models.CharField(max_length=120)
    subtitle      = models.CharField(max_length=255, blank=True)
    icon          = models.CharField(max_length=50, default="fas fa-percent")
    highlight     = models.CharField(max_length=60, blank=True)   # “Limited Time…”
    start_date    = models.DateField(default=timezone.now)
    end_date      = models.DateField(null=True, blank=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    title       = models.CharField(max_length=200)
    # slug        = models.SlugField(unique=True)
    slug = models.SlugField(unique=True, max_length=200)
    cover       = models.ImageField(upload_to="blog_covers", blank=True, null=True)
    excerpt     = models.TextField(max_length=300)
    body        = models.TextField()
    category    = models.CharField(max_length=80, default="General")
    published   = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-published"]

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    name        = models.CharField(max_length=80)
    role        = models.CharField(max_length=80)
    quote       = models.TextField(max_length=400)
    rating      = models.PositiveSmallIntegerField(default=5)          # 1‑5
    avatar      = models.ImageField(upload_to="testimonials", blank=True, null=True)
    is_featured = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} • {self.role}"
    
# models.py
from django.db import models

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email    
