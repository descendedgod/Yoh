from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    show_last_seen = models.BooleanField(default=True)
    show_online_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar if it exists
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def display_name(self):
        return self.full_name
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

class Friendship(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='user_friends', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'friend')
        indexes = [
            models.Index(fields=['user', 'friend']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('voice', 'Voice'),
    ]
    
    DELIVERY_STATUS = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    file_attachment = models.FileField(upload_to='messages/files/', blank=True, null=True)
    image_attachment = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    voice_attachment = models.FileField(upload_to='messages/voice/', blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_STATUS, default='sent')
    
    # Message reactions (like WhatsApp reactions)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] if self.content else f"[{self.message_type}]"
        return f"From {self.sender.username} to {self.receiver.username}: {content_preview}"
    
    def save(self, *args, **kwargs):
        if self.is_read and not self.read_at:
            self.read_at = timezone.now()
            self.delivery_status = 'read'
        elif not self.is_read and self.delivery_status == 'sent':
            self.delivery_status = 'delivered'
        
        super().save(*args, **kwargs)
    
    @property
    def is_media_message(self):
        return self.message_type in ['image', 'file', 'voice']
    
    def get_attachment_url(self):
        if self.image_attachment:
            return self.image_attachment.url
        elif self.file_attachment:
            return self.file_attachment.url
        elif self.voice_attachment:
            return self.voice_attachment.url
        return None

class MessageReaction(models.Model):
    REACTION_TYPES = [
        ('👍', 'Thumbs Up'),
        ('❤️', 'Heart'),
        ('😂', 'Laughing'),
        ('😮', 'Wow'),
        ('😢', 'Sad'),
        ('😡', 'Angry'),
    ]
    
    message = models.ForeignKey(Message, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user')
        indexes = [
            models.Index(fields=['message', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to message {self.message.id}"

class ChatGroup(models.Model):
    """For future group chat functionality"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='groups/', blank=True, null=True)
    members = models.ManyToManyField(User, through='GroupMembership')
    created_by = models.ForeignKey(User, related_name='created_groups', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('group', 'user')

class BlockedUser(models.Model):
    """Handle blocked users"""
    blocker = models.ForeignKey(User, related_name='blocked_users', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    blocked_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('blocker', 'blocked')
    
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"

class TypingStatus(models.Model):
    """Track typing status for real-time indicators"""
    user = models.ForeignKey(User, related_name='typing_to', on_delete=models.CASCADE)
    typing_to = models.ForeignKey(User, related_name='being_typed_to', on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'typing_to')
    
    def __str__(self):
        status = "typing" if self.is_typing else "not typing"
        return f"{self.user.username} is {status} to {self.typing_to.username}"