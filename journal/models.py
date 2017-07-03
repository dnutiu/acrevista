from django.db import models
from django.contrib.auth.models import User
from .validators import FileValidator


class Paper(models.Model):
    user = models.ForeignKey(User, related_name='papers')
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(max_length=2000, blank=False)
    validate_file = FileValidator(max_size=1024 * 1024 * 50,  # Max size is 50Mb
                                  content_types=('application/pdf', 'text/html', 'application/msword',
                                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                                 'application/vnd.ms-powerpoint',
                                                 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                                                 'text/plain',))
    file = models.FileField(upload_to='papers', blank=False, validators=[validate_file])
