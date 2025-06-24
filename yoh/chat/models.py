from django.db import models
from  django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class Friendship(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='user_friends', on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'friend')


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_message', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} : {self.content[:7]}...."
    
