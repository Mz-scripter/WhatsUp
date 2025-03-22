from django.urls import path
from . import views


urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('chat/<int:chat_room_id>/', views.chat_detail, name='chat_detail'),
    path('create_one_on_one/<int:user_id>/', views.create_one_on_one_chat, name='create_one_on_one'),
    path('create_group/', views.create_group_chat, name='create_group'),
    path('chat/<int:chat_room_id>/add_participants/', views.add_participants, name='add_participants'),
    path('chat/<int:chat_room_id>/remove_participants/<int:user_id>/', views.remove_participants, name='remove_participants'),
    path('chat/<int:chat_room_id>/designate_admin/<int:user_id>/', views.designate_admin, name='designate_admin'),
    path('chat/<int:chat_room_id>/remove_admin/<int:user_id>/', views.remove_admin, name='remove_admin'),
    path('chat/<int:chat_room_id>/rename/', views.rename_chat_room, name='rename_chat_room'),
    path('chat/<int:chat_room_id>/delete/', views.delete_chat_room, name='delete_chat_room'),
    path('chat/<int:chat_room_id>/management/', views.chat_management, name='chat_management'),
]