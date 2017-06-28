from django.contrib import admin
from .models import Paper


class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'file_link']

    def file_link(self, obj):
        if obj.file:
            return "<a href='%s' download>Download</a>" % (obj.file.url,)
        else:
            return "No attachment"

    file_link.allow_tags = True
    file_link.short_description = 'File Download'


admin.site.register(Paper, PaperAdmin)
