"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.contrib import messages
from django.shortcuts import render
from .forms import SubmitPaperForm


# TODO: PROFILE, HISTORY, REVIEW PAGES
# Homepage of the Journal
def homepage(request):
    return render(request, "journal/index.html", {'section': 'journal'})


def submit_paper(request):
    if request.method == 'POST':
        form = SubmitPaperForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Paper submitted successfully!")
        else:
            messages.warning(request, "Error submitting paper!")
    else:
        form = SubmitPaperForm()
    return render(request, "journal/submit.html", {'section': 'journal', 'form': form})
