from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom
from django.contrib.auth.models import User


@login_required
def create_one_on_one_chat(request, user_id):
    other_user = User.objects.get(id=user_id)
    chat_room = ChatRoom.objects.create(is_group_chat=False)
    chat_room.participants.add(request.user, other_user)
    return redirect('chat_detail', chat_room_id=chat_room.id)

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        name = request.POST.get('group_name')
        chat_room = ChatRoom.objects.create(name=name, is_group_chat=True)
        chat_room.participants.add(request.user)
        return redirect('chat_detail', chat_room_id=chat_room.id)
    return render(request, 'chats/create_group.html')

@login_required
def chat_list(request):
    chat_rooms = request.user.chat_rooms.all()
    return render(request, 'chats/chat_list.html', {'chat_rooms': chat_rooms})

@login_required
def chat_detail(request, chat_room_id):
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    return render(request, 'chats/chat_detail.html', {'chat_room': chat_room})