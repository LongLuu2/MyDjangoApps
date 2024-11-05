from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    profile_image_url = models.URLField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    def get_status_messages(self):
        return self.status_messages.order_by('-timestamp')
    
    def get_friends(self):
        friends_from_profile1 = Friend.objects.filter(profile1=self)
        friends_from_profile2 = Friend.objects.filter(profile2=self)
        
        friends = []
        for friend in friends_from_profile1:
            friends.append(friend.profile2)  
        for friend in friends_from_profile2:
            friends.append(friend.profile1)  
        return friends
    def add_friend(self, other):
        if self == other:
            return

        friendship_exists = Friend.objects.filter(
            models.Q(profile1=self, profile2=other) | models.Q(profile1=other, profile2=self)
        ).exists()

        if not friendship_exists:
            Friend.objects.create(profile1=self, profile2=other)

    def get_friend_suggestions(self):
        friends = self.get_friends()
        all_profiles = Profile.objects.exclude(pk=self.pk).exclude(pk__in=[friend.pk for friend in friends])
        return all_profiles
    
    def get_news_feed(self):
        friends = self.get_friends()
        profiles_to_include = [self] + friends
        return StatusMessage.objects.filter(profile__in=profiles_to_include).order_by('-timestamp')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class StatusMessage(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="status_messages")

    def get_images(self):
        return Image.objects.filter(status_message=self)
    
    def __str__(self):
        return f"Msg by {self.profile.first_name}: {self.message[:20]}..." 
    
class Image(models.Model):
    image_file = models.ImageField(upload_to='images/')  
    status_message = models.ForeignKey('StatusMessage', on_delete=models.CASCADE)  
    timestamp = models.DateTimeField(default=timezone.now)
      

    def __str__(self):
        return self.image_file.name

class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile1")
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile2")
    timestamp = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}"
