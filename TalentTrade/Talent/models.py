from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

class Categories(models.Model): 
    name = models.CharField(max_length=128)  

    def __str__(self):
        return self.name


class UserAccount(models.Model):
    # Connect to User - ONE user has ONE profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Why OneToOne? Because 1 user = 1 profile (not many profiles)
    
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # DON'T add email here - User already has email!
    # Access it with: user.email
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class TalentsPost(models.Model):  
    # Connect to User - ONE user can have MANY posts
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Why ForeignKey? Because 1 user can create many posts
    
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    
    name = models.CharField(max_length=128)  # Service name
    description = models.TextField()
    phone_number = models.CharField(max_length=20)
    
    # DON'T store email here - get it from user.email
    
    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:  # Only when NEW user is created
        UserAccount.objects.create(user=instance)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username}: {self.content[:20]}'