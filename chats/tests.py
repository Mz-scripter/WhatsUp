from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from chats.models import ChatRoom, Message
from channels.testing import WebsocketCommunicator
from chats.consumers import ChatConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack

# Set up the WebSocket application for testing
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/chat/<int:room_id>/', ChatConsumer.as_asgi()),
        ])
    ),
})


class ChatAppTests(TestCase):
    def setUp(self):
        """
        Set up a user and log them in before each test.
        """
        self.user = User.objects.create_user('testuser', 'test@gmail.com', 'password123')
        self.client.login(username='testuser', password='password123')
    
    def test_chat_list_view(self):
        """
        Test that the chat list view returns the correct template.
        """
        response = self.client.get(reverse('chat_list'))
        self.assertTemplateUsed(response, 'chats/chat_list.html')
    
    def test_create_chat_room(self):
        """
        Test that a logged-in user can create a chat room.
        """
        response = self.client.post(reverse('create_group'), {
            'group_name': 'Test Room',
            'participants': '1'
        })
        self.assertEqual(ChatRoom.objects.count(), 1)
        chat_room = ChatRoom.objects.get(name='Test Room')
        self.assertIn(self.user, chat_room.participants.all())