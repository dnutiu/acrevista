from django.db import models
from django.contrib.auth.models import User


class Paper(models.Model):
    user = models.ForeignKey(User, related_name='papers')
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(max_length=2000, blank=False)
    file = models.FileField(upload_to='papers', blank=False)
