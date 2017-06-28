from django import forms
from .models import Paper


# Allows the submission of a paper.
class SubmitPaperForm(forms.ModelForm):
    class Meta: # TODO: VALIDATE FILE EXTENSIONS. SET MAX SIZE?
        model = Paper
        fields = ('title', 'description', 'file')
