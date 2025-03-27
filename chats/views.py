from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from django.contrib.auth.models import User
from .forms import MessageForm
from django.http import HttpResponseForbidden
from django.contrib import messages

@login_required
def new_chat(request):
    page = 'no_footer'
    users = User.objects.exclude(id=request.user.id)
    context = {
        'users': users,
        'page': page,
    }
    return render(request, 'chats/new_chat.html', context)

@login_required
def create_one_on_one_chat(request, user_id):
    other_user = User.objects.get(id=user_id)
    chat_room = ChatRoom.objects.create(is_group_chat=False)
    chat_room.participants.add(request.user, other_user)
    return redirect('chat_detail', chat_room_id=chat_room.id)

@login_required
def create_group_chat(request):
    page = 'no_footer'
    request.session['previous_page'] = request.META.get('HTTP_REFERER')
    users = User.objects.exclude(id=request.user.id)
    
    if request.method == 'POST':
        name = request.POST.get('group_name')
        participant_ids = request.POST.getlist('participants', '')
        
        participant_ids = [int(id) for id in participant_ids[0].split(',')]
        
        chat_room = ChatRoom.objects.create(name=name, is_group_chat=True, owner=request.user)
        chat_room.participants.add(request.user)
        chat_room.admins.add(request.user)
        
        selected_users = User.objects.filter(id__in=participant_ids)
        chat_room.participants.add(*selected_users)
        return redirect('chat_detail', chat_room_id=chat_room.id)
    
    context = {
        'users': users,
        'page': page,
    }
    return render(request, 'chats/create_group.html', context)

@login_required
def add_participants(request, chat_room_id):
    page = 'no_footer'
    request.session['previous_page'] = request.META.get('HTTP_REFERER')
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    users = User.objects.exclude(id__in=chat_room.participants.values_list('id', flat=True))
    
    if not chat_room.is_group_chat:
        return HttpResponseForbidden("Cannot add participants to one-on-one chat.")
    
    if request.user not in chat_room.admins.all():
        return HttpResponseForbidden("Only admins can add participants.")
    
    if request.method == 'POST':
        participant_ids = request.POST.getlist('participants', '')
        
        participant_ids = [int(id) for id in participant_ids[0].split(',')]
        
        selected_users = User.objects.filter(id__in=participant_ids)
        chat_room.participants.add(*selected_users)
        return redirect('chat_management', chat_room_id=chat_room.id)
    
    context = {
        'chat_room': chat_room,
        'users': users,
        'page': page,
    }
    return render(request, 'chats/add_participants.html', context)

@login_required
def remove_participants(request, chat_room_id, user_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    user = get_object_or_404(User, id=user_id)
    
    if not chat_room.is_group_chat:
        return HttpResponseForbidden("Cannot remove participants from one-on-one chat.")
    
    if request.user not in chat_room.admins.all():
        return HttpResponseForbidden("Only admins can remove participants.")
    
    chat_room.participants.remove(user)
    if request.user in chat_room.admins.all():
        chat_room.admins.remove(user)
    return redirect('chat_management', chat_room_id=chat_room.id)
    
@login_required
def designate_admin(request, chat_room_id, user_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    user = get_object_or_404(User, id=user_id)
    
    if not chat_room.is_group_chat:
        return HttpResponseForbidden("Cannot designate admins in one-on-one chat.")
    
    if request.user not in chat_room.admins.all():
        return HttpResponseForbidden("Only admins can designate other admins.")
    
    chat_room.admins.add(user)
    return redirect('chat_management', chat_room_id=chat_room.id)

@login_required
def remove_admin(request, chat_room_id, user_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    user = get_object_or_404(User, id=user_id)
    
    if not chat_room.is_group_chat:
        return HttpResponseForbidden("Cannot designate admins in one-on-one chat.")
    
    if request.user not in chat_room.admins.all():
        return HttpResponseForbidden("Only admins can designate other admins.")
    
    chat_room.admins.remove(user)
    return redirect('chat_management', chat_room_id=chat_room.id)

@login_required
def rename_chat_room(request, chat_room_id):
    request.session['previous_page'] = request.META.get('HTTP_REFERER')
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    
    if not chat_room.is_group_chat:
        return HttpResponseForbidden("Cannot rename one-on-one chat.")
    
    if request.user not in chat_room.admins.all():
        return HttpResponseForbidden("Only admins can rename the chat.")
    
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if new_name:
            chat_room.name = new_name
            chat_room.save()
            messages.success(request, "Chat room renamed successfully.")
        return redirect('chat_detail', chat_room_id=chat_room.id)
    return render(request, 'chats/rename_chat_room.html', {'chat_room': chat_room})

@login_required
def delete_chat_room(request, chat_room_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    
    if not chat_room.is_group_chat:
        return HttpResponseForbidden("Cannot delete one-on-one chat.")
    
    if request.user not in chat_room.admins.all():
        return HttpResponseForbidden("Only admins can delete the chat.")
    
    if request.method == 'POST':
        chat_room.delete()
        messages.success(request, "Chat room deleted successfully.")
        return redirect('chat_list')
    return render(request, 'chats/delete_chat_room.html', {'chat_room': chat_room})
        

@login_required
def chat_list(request):
    chat_rooms = request.user.chat_rooms.all()
    for chat_room in chat_rooms:
        unread_count = chat_room.messages.exclude(read_by=request.user).count()
        chat_room.unread_count = unread_count
        last_message = Message.objects.filter(chat_room=chat_room).order_by('-timestamp').first()
        chat_room.last_message = last_message.content if last_message else "No messages yet"
        chat_room.last_message_time = last_message.timestamp if last_message else None
    return render(request, 'chats/chat_list.html', {'chat_rooms': chat_rooms})

@login_required
def chat_detail(request, chat_room_id):
    page = 'no_footer'
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    chat_name = chat_room.get_chat_name(request.user)
    if request.user not in chat_room.participants.all():
        return HttpResponseForbidden("You are not a participant in this chat room.")
    chat_messages = Message.objects.filter(chat_room=chat_room).visible_to(request.user).order_by('timestamp')
    
    for message in chat_messages:
        message.read_by.add(request.user)
            
    form = MessageForm()
    context = {
        'chat_room': chat_room,
        'chat_messages': chat_messages,
        'form': form,
        'chat_name': chat_name,
        'page': page,
    }
    return render(request, 'chats/chat_detail.html', context)

@login_required
def chat_management(request, chat_room_id):
    page = 'no_footer'
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    chat_name = chat_room.get_chat_name(request.user)
    participants = chat_room.participants.all()

    context = {
        'chat_room': chat_room,
        'chat_name': chat_name,
        'participants': participants,
        'page': page,
    }
    return render(request, 'chats/chat_management.html', context)