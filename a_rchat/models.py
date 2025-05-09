from django.db import models
from django.contrib.auth.models import User
import shortuuid
from django.conf import settings

def generate_group_name():
    return shortuuid.uuid()

class ChatGroup(models.Model):
    group_name = models.CharField(
        max_length=100,
        unique=True,
        default=generate_group_name,
    )
    admin = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name='groupchats',blank=True,null=True)
    groupchat_name = models.CharField(max_length=100,blank=True,null=True)
    users_online = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='online_in_groups',blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='chat_groups',blank=True)
    is_private = models.BooleanField(default=False)



    def __str__(self):
        return self.group_name


class GroupMessage(models.Model):
    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}: {self.body}"

    class Meta:
        ordering = ['-created']