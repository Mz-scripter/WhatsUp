import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom
from django.contrib.auth.models import User
from channels.db import database_sync_to_async


@database_sync_to_async
def get_chat_room(room_id):
    return ChatRoom.objects.get(id=room_id)

@database_sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)

@database_sync_to_async
def create_message(chat_room, sender, content, is_anonymous):
    return Message.objects.create(
        chat_room=chat_room,
        sender=sender,
        content=content,
        is_anonymous=is_anonymous
    )


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        sender_id = text_data_json['sender_id']
        is_anonymous = text_data_json.get('is_anonymous', False)
        
        # Save message to database
        sender = await get_user(sender_id)
        chat_room = await get_chat_room(self.room_id)
        msg = await create_message(
            chat_room=chat_room,
            sender=sender,
            content=message_content,
            is_anonymous=is_anonymous and chat_room.is_group_chat
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg.content,
                'sender': msg.get_sender_display(),
                'timestamp': msg.timestamp.isoformat()
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))