from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom
from django.contrib.auth.models import User
from .forms import MessageForm
from django.http import HttpResponseForbidden


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
    
    if request.user not in chat_room.participants.all():
        return HttpResponseForbidden("You are not a participant in this chat room.")
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat_room = chat_room
            message.sender = request.user
            if not chat_room.is_group_chat:
                message.is_anonymous = False
            message.save()
            return redirect('chat_detail', chat_room_id=chat_room.id)
    else:
        form = MessageForm()
    
    messages = chat_room.messages.order_by('timestamp')
    context = {
        'chat_room': chat_room,
        'messages': messages,
        'form': form,
    }
    return render(request, 'chats/chat_detail.html', context)