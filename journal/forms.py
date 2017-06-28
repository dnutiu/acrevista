from django import forms
from .models import Paper


# Allows the submission of a paper.
class SubmitPaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ('title', 'description', 'file')
