from django import forms
from .models import Paper


# Allows the submission of a paper.
class SubmitPaperForm(forms.ModelForm):

    supplementary_materials = forms.FileField(required=False)

    class Meta:
        model = Paper
        fields = ('title', 'description', 'manuscript', 'cover_letter', 'supplementary_materials')
