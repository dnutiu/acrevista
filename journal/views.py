"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import SubmitPaperForm
from .validators import validate_authors

# Homepage of the Journal
def homepage(request):
    return render(request, "journal/index.html", {'section': 'journal'})


@login_required
def submit_paper(request):
    if request.method == 'POST':
        form = SubmitPaperForm(data=request.POST, files=request.FILES)
        # Construct Author objects.
        authors = [request.POST.getlist('authors_first_name'), request.POST.getlist('authors_last_name'),
                   request.POST.getlist('authors_email'), request.POST.getlist('authors_affiliation'),
                   request.POST.getlist('authors_country')]

        if form.is_valid() and validate_authors(*authors):
            paper = form.save(commit=False)
            paper.user = request.user

            # Add authors to the text area
            data = list(zip(*authors))
            for author in data:
                paper.authors += str(author) + "\n"

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
