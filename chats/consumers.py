import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta


@database_sync_to_async
def get_chat_room(room_id):
    return ChatRoom.objects.get(id=room_id)

@database_sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)

@database_sync_to_async
def create_message(chat_room, sender, content, is_anonymous, reply_to=None):
    msg =  Message.objects.create(
        chat_room=chat_room,
        sender=sender,
        is_anonymous=is_anonymous,
        reply_to=reply_to
    )
    msg.content = content
    msg.save()
    return msg


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
                    'message_id': msg.id,
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
        
        elif event_type == 'delete_message':
            await self.handle_delete_message(text_data_json)
        elif event_type == 'edit_message':
            await self.handle_edit_message(text_data_json)
        elif event_type == 'reply_message':
            await self.handle_reply_message(text_data_json)

    async def chat_message(self, event):
        # Send message to WebSocket
        message_data = {
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'read_by': event.get('read_by', [])
        }
        
        if 'reply_to_id' in event:
            message_data['reply_to_id'] = event['reply_to_id']
            message_data['reply_to_sender'] = event['reply_to_sender']
            message_data['reply_to_content'] = event['reply_to_content']
        
        await self.send(text_data=json.dumps(message_data))
            
    
    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_event',
            'sender': event['sender'],
            'is_typing': event['is_typing']
        }))
    
    async def handle_delete_message(self, data):
        message_id = data['message_id']
        scope = data['scope']
        
        msg = await database_sync_to_async(Message.objects.select_related('sender').get)(id=message_id)
        
        if scope == 'me':
            await database_sync_to_async(msg.deleted_for.add)(self.user)
            await self.send(text_data=json.dumps({
                'type': 'message_deleted',
                'message_id': msg.id,
                'scope': 'me',
                'user_id': self.user.id
            }))
        elif scope == 'everyone':
            time_elapsed = timezone.now() - msg.timestamp
            is_sender = self.user == msg.sender
            is_admin = await database_sync_to_async(lambda: self.user in msg.chat_room.admins.all())()
            if (is_sender or is_admin) and time_elapsed < timedelta(minutes=15):
                msg.is_deleted = True
                await database_sync_to_async(msg.save)()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_deleted',
                        'message_id': msg.id,
                        'scope': 'everyone'
                    }
                )
    
    async def handle_edit_message(self, data):
        message_id = data['message_id']
        new_content = data['new_content']
        
        msg = await database_sync_to_async(Message.objects.select_related('sender').get)(id=message_id)
        time_elapsed = timezone.now() - msg.timestamp
        
        if self.user == msg.sender and time_elapsed < timedelta(minutes=15):
            msg.content = new_content
            msg.edited_at = timezone.now()
            await database_sync_to_async(msg.save)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_edited',
                    'message_id': msg.id,
                    'new_content': msg.content,
                    'edited_at': msg.edited_at.isoformat()
                }
            )
    
    async def handle_reply_message(self, data):
        reply_to_id = data['reply_to_id']
        message_content = data['message']
        
        is_anonymous = data.get('is_anonymous', False)
        
        chat_room = await get_chat_room(self.room_id)
        reply_to_msg = await database_sync_to_async(Message.objects.select_related('sender').get)(id=reply_to_id)
        
        msg = await create_message(
            chat_room=chat_room,
            sender=self.user,
            content=message_content,
            is_anonymous=is_anonymous and chat_room.is_group_chat,
            reply_to=reply_to_msg,
        )
        
        timestamp_str = msg.timestamp.strftime("%I:%M%p")
        formatted_time = timestamp_str.lstrip('0')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': msg.id,
                'message': msg.content,
                'sender': msg.get_sender_display(),
                'timestamp': formatted_time,
                'reply_to_id': reply_to_msg.id,
                'reply_to_sender': reply_to_msg.sender.username,
                'reply_to_content': reply_to_msg.content[:50],
                'read_by': [self.user.id]
            }
        )

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps(event))

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