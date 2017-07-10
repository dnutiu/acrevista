from django import forms
from .models import Paper, Review


# Allows the submission of a paper.
class SubmitPaperForm(forms.ModelForm):

    supplementary_materials = forms.FileField(required=False)

    class Meta:
        model = Paper
        fields = ('title', 'description', 'manuscript', 'cover_letter', 'supplementary_materials')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('appropriate', 'recommendation', 'comment', 'confidential_comment', 'additional_file')