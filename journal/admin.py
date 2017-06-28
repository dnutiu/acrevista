from django.contrib import admin
from .models import Paper


class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'user']


admin.site.register(Paper, PaperAdmin)
