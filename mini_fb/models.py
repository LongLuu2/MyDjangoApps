from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    profile_image_url = models.URLField(max_length=200)
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    def get_status_messages(self):
        return self.status_messages.order_by('-timestamp')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class StatusMessage(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="status_messages")

    def __str__(self):
        return f"Msg by {self.profile.first_name}: {self.message[:20]}..." 