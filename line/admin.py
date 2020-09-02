from django.contrib import admin
from .models import QNA, Follower


class QNAadmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'learned_from', ]
admin.site.register(QNA, QNAadmin)

class Followeradmin(admin.ModelAdmin):
    list_display = ['user_id', 'display_name', 'picture_url', 'status_message', 'timestamp', 'state', ]
admin.site.register(Follower, Followeradmin)