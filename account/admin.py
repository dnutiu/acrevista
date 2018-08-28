from django.contrib import admin
from .models import Profile

# ProfileAdmin enables the model Profile to be shown in the admin view.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']


admin.site.register(Profile, ProfileAdmin)
