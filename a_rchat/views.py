from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
# Create your views here.


@login_required
def chat_view(request,chatroom_name='public-chat'):

    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else :
                messages.warning(request,'You need to verify your email address.')
                return redirect('profile-emailverify')

    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message': message,
                'user':request.user,
            }

            return render(request, 'a_rchat/partials/chat_message_p.html', context)

    context = {
        'chat_group':chat_group,
        'chat_messages': chat_messages,
        'form': form,
        'chatroom_name':chatroom_name,
        'other_user':other_user,
    }
    return render(request, 'a_rchat/chat.html',context)


@login_required
def get_or_create_chatroom(request,username):
    if request.user.username == username:
        return redirect('home')

    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user,request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)

    return redirect('chatroom',chatroom_name=chatroom.group_name)



@login_required
def create_chatgroup(request):
    form = NewGroupForm()
    context = {
        'form':form,
    }
    if request.method == 'POST':
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.admin = request.user
            new_group.save()
            new_group.members.add(request.user)
            return redirect('chatroom',new_group.group_name)
    return render(request,'a_rchat/create_groupchat.html',context)


def chatroom_edit_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404
    if request.method == "POST":
        form = CharRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)

            return redirect('chatroom',chatroom_name=chatroom_name)

    form = CharRoomEditForm(instance=chat_group)
    context = {
        'chat_group':chat_group,
        'form':form,
    }
    return render(request,'a_rchat/chatroom_edit.html',context)

def chatroom_remove_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404
    if request.method == "POST":
        chat_group.delete()
        messages.success(request,'Chat room deleted.')
        return redirect('home')
    context = {
        'chat_group': chat_group,
    }
    return render(request,'a_rchat/chatroom_delete.html',context)