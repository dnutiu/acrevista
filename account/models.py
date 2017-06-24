from django.db import models
from django.conf import settings

# Create your models here.


# The Profile class extends Django's default user model.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    first_name = models.CharField(blank=False, max_length=30)
    last_name = models.CharField(blank=False, max_length=30)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.CharField(max_length=1024)

    def __srt__(self):
        return "Profile of user: {}".format(self.user.username)
