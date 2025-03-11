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
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
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
        event_type = text_data_json.get('type')
        
        if not self.user.is_authenticated:
            return
        
        if event_type == 'chat_message':
            message_content = text_data_json.get('message')
            is_anonymous = text_data_json.get('is_anonymous', False)
            
            chat_room = await get_chat_room(self.room_id)
            msg = await create_message(
                chat_room=chat_room,
                sender=self.user,
                content=message_content,
                is_anonymous=is_anonymous and chat_room.is_group_chat
            )
            await database_sync_to_async(msg.read_by.add)(self.user)
            
            timestamp_str = msg.timestamp.strftime("%I:%M%p")
            formatted_time = timestamp_str.lstrip('0')
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg.content,
                    'sender': msg.get_sender_display(),
                    'timestamp': formatted_time,
                    'read_by': [self.user.id]
                }
            )
            
            participants = await database_sync_to_async(list)(chat_room.participants.exclude(id=self.user.id))
            for participant in participants:
                unread_count = await database_sync_to_async(chat_room.messages.exclude(read_by=participant).count)()
                await self.channel_layer.group_send(
                    f"user_{participant.id}_notifications",
                    {
                        'type': 'notification_event',
                        'chat_room_id': chat_room.id,
                        'unread_count': unread_count,
                        'message': f"New message in {chat_room.name}",
                    }
                )
        
        elif event_type == 'typing':
            is_typing = text_data_json.get('is_typing', False)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_event',
                    'sender': self.user.username,
                    'is_typing': is_typing
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'read_by': event['read_by']
        }))
    
    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_event',
            'sender': event['sender'],
            'is_typing': event['is_typing']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        self.group_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self,close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def notification_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'chat_room_id': event['chat_room_id'],
            'unread_count': event['unread_count'],
            'message': event['message'],
        }))