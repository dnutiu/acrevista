from django.db import models
from django.conf import settings

# Create your models here.


# The Profile class extends Django's default user model.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=4094)

    def __srt__(self):
        return "Profile of user: {}".format(self.user.username)
