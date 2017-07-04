"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import SubmitPaperForm


# Homepage of the Journal
def homepage(request):
    return render(request, "journal/index.html", {'section': 'journal'})


@login_required
def submit_paper(request):
    if request.method == 'POST':
        form = SubmitPaperForm(data=request.POST, files=request.FILES)
        fns = request.POST.getlist('authors_first_name')
        lns = request.POST.getlist('authors_last_name')
        ems = request.POST.getlist('authors_email')
        print(fns, lns, ems)
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
