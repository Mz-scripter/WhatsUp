from django.urls import path
from . import views


urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('chat/<int:chat_room_id>/', views.chat_detail, name='chat_detail'),
    path('create_one_on_one/<int:user_id>/', views.create_one_on_one_chat, name='create_one_on_one'),
    path('create_group/', views.create_group_chat, name='create_group'),
]