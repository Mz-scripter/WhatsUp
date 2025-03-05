from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_group_chat = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    
    def __str__(self):
        if self.is_group_chat:
            return self.name or "Unnamed Group Chat"
        else:
            users = self.participants.all()
            return f"Chat between {users[0].username} and {users[1].username}"


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat_room}"