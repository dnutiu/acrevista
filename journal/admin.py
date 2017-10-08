from django.contrib import admin
from .models import Paper, Review


class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'file_link', 'cover_letter_link', 'created']
    search_fields = ['title', 'user']
    # Add raw_id_fields = ('user',) if you want to be able to search for users.

    @classmethod
    def file_link(self, obj):
        if obj.manuscript:
            return "<a href='{}' download>Download</a>".format(obj.manuscript.url)
        else:
            return "No attachment"

    file_link.allow_tags = True
    file_link.short_description = 'Manuscript'

    @classmethod
    def cover_letter_link(self, obj):
        if obj.cover_letter:
            return "<a href='{}' download>Download</a>".format(obj.cover_letter.url)
        else:
            return "No attachment"

    cover_letter_link.allow_tags = True
    cover_letter_link.short_description = 'Cover Letter'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'paper', 'recommendation', 'appropriate', 'created']


admin.site.register(Paper, PaperAdmin)
admin.site.register(Review, ReviewAdmin)
