from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    pass

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    pass