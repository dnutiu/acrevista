from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/{1}'.format(instance.user.id, filename)


class Paper(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='papers')
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(max_length=500, blank=False)
    file = models.FileField(upload_to=user_directory_path, blank=False)
