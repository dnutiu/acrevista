"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.contrib import messages
from django.shortcuts import render
from .forms import SubmitPaperForm


# Homepage of the Journal
def homepage(request):
    return render(request, "journal/index.html", {'section': 'journal'})


def submit_paper(request):
    if request.method == 'POST':
        form = SubmitPaperForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.user = request.user
            paper.save()
            messages.success(request, "Paper submitted successfully!")
        else:
            messages.warning(request, "Error submitting paper!")
    else:
        form = SubmitPaperForm()
    return render(request, "journal/submit.html", {'section': 'journal', 'form': form})


def profile(request):
    return render(request, 'journal/profile.html', {'section': 'journal'})


def history(request):
    return render(request, 'journal/history.html', {'section': 'journal'})


def review(request):
    return render(request, 'journal/review.html', {'section': 'journal'})
