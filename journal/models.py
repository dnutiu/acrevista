from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from .validators import FileValidator


# This function is used by the Paper model class.
def user_id_path(instance, filename):
    """
    Constructs a path of the type /papers/<user_id>_<username>/<paper title>/<filename>

    instance: The instance provide dy django
    filename: The filename provided by django

    returns: A string containing the path of the uploaded paper.
    """
    return "papers/{0}_{3}/{1}/{2}".format(instance.user.id, instance.title, filename, instance.user.username)


class Paper(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('under_review', 'Under Review'),
        ('preliminary_reject', 'Preliminary Reject'),
        ('accepted', 'Accepted'),
    )
    user = models.ForeignKey(User, related_name='papers')
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(max_length=2000, blank=False)
    authors = models.TextField(max_length=4096)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='processing')
    # File validator.
    validate_file = FileValidator(max_size=1024 * 1024 * 50,  # Max size is 50Mb
                                  content_types=('application/pdf', 'text/html', 'application/msword',
                                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.'
                                                 'document',
                                                 'text/plain',))
    manuscript = models.FileField(upload_to=user_id_path, blank=False, validators=[validate_file])
    cover_letter = models.FileField(upload_to=user_id_path, blank=False, validators=[validate_file])
    supplementary_materials = models.FileField(upload_to=user_id_path, blank=True, null=True, default=None,
                                               validators=[validate_file])

    class Meta:
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse('journal:paper_detail', args=[str(self.id)])

    def __str__(self):
        return self.title
