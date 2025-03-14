from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_group_chat = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    admins = models.ManyToManyField(User, related_name='admin_chat_rooms', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_chat_rooms', null=True)
    
    def __str__(self):
        if self.is_group_chat:
            return self.name or "Unnamed Group Chat"
        else:
            users = self.participants.all()
            participants_count = users.count()
            if participants_count == 0:
                return "Empty Chat"
            elif participants_count == 1:
                return f"Chat with {users[0].username}"
            else:
                return f"Chat Between {users[0].username} and {users[1].username}"


class MessageQuerySet(models.QuerySet):
    def visible_to(self, user):
        return self.exclude(is_deleted=True).exclude(deleted_for=user)


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_for = models.ManyToManyField(User, related_name='deleted_messages', blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    objects = MessageQuerySet.as_manager()
    
    def __str__(self):
        sender_display = "Anonymous" if self.is_anonymous else self.sender.username
        return f"Message from {sender_display} in {self.chat_room}"
    
    def clean(self):
        super().clean()
        if not self.content or not self.content.strip():
            raise ValidationError("Message content cannot be empty.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def get_sender_display(self):
        return "Anonymous" if self.is_anonymous else self.sender.username
