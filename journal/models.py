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


# This function is used by the Paper model class.
def review_user_id_path(instance, filename):
    """
    Constructs a path of the type /review/<user_id>_<username>/<filename

    instance: The instance provide dy django
    filename: The filename provided by django

    returns: A string containing the path of the uploaded paper.
    """
    return "papers/{0}/{1}/{2}".format(instance.user.id, instance.user.username, filename)


# File validator.
validate_file = FileValidator(max_size=1024 * 1024 * 50,  # Max size is 50Mb
                              content_types=('application/pdf', 'text/html', 'application/msword',
                                             'application/vnd.openxmlformats-officedocument.wordprocessingml.'
                                             'document',
                                             'text/plain',))


class Paper(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('under_review', 'Under Review'),
        ('preliminary_reject', 'Preliminary Reject'),
        ('accepted', 'Accepted'),
    )
    user = models.ForeignKey(User, related_name='papers')
    editor = models.ForeignKey(User, blank=True, null=True, related_name='editor_papers')
    title = models.CharField(max_length=64, blank=False)
    # Paper info
    description = models.TextField(max_length=2000, blank=False, help_text="Represents the abstract of the paper.")
    authors = models.TextField(max_length=4096,
                               help_text="Each row represents an author that follows this template: (First Name, "
                                         "Last Name, Email, Affiliation, Country, Corresponding Author)")
    reviewers = models.ManyToManyField(User, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='processing')
    # Files
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


# Each paper can have multiple reviews
class Review(models.Model):
    APPROPRIATE_CHOICES = (
        ('appropriate', 'The topic of this manuscript falls within the scope of the journal.'),
        ('not_appropriate', 'The topic of this manuscript does not fall within the scope of the journal.'),
    )
    RECOMMENDATION_CHOICES = (
        ('0', 'Consider after Major Changes.'),
        ('+2', 'Publish Unaltered.'),
        ('+1', 'Consider after Minor Changes.'),
        ('-1', 'Reject. (Paper is not of sufficient quality or novelty to be published in this journal)'),
        ('-2', 'Reject. (Paper is seriously flawed; Do not encourage resubmission)'),
    )

    user = models.ForeignKey(User, related_name='reviews')  # The submitter
    paper = models.ForeignKey(Paper, related_name='reviews')
    created = models.DateTimeField(auto_now_add=True)
    editor_review = models.BooleanField()

    appropriate = models.CharField(max_length=64, choices=APPROPRIATE_CHOICES, default=None)
    recommendation = models.CharField(max_length=64, choices=RECOMMENDATION_CHOICES, default=None)

    comment = models.TextField(max_length=32768, help_text="This comment will be shown to the author.")
    confidential_comment = models.TextField(max_length=32768,
                                            help_text="This comment will not be shown to the author.")

    additional_file = models.FileField(upload_to=review_user_id_path, blank=True, validators=[validate_file])

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "{}'s review of {}".format(self.user.username, self.paper.title)
