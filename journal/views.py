"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import SubmitPaperForm, ReviewForm
from .validators import validate_authors
from django.http import Http404
from .models import Paper


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
                   request.POST.getlist('authors_country'), request.POST.getlist('authors_corresponding')]

        if form.is_valid() and validate_authors(*authors):
            paper = form.save(commit=False)
            paper.user = request.user

            # Add authors to the text area
            data = list(zip(*authors))
            for author in data:
                paper.authors += str(author) + "\n"

            paper.save()
            messages.success(request, "Paper submitted successfully!")
            return render(request, "journal/submit_done.html", {'section': 'journal', 'paper': paper})
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


@login_required
def paper_detail(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    can_review = request.user in paper.reviewers.all()

    # Raise 404 if we're looking at someone's else paper and we're not the author or reviewers
    if not can_review and request.user != paper.user:
        raise Http404

    reviews = paper.reviews.all()  # Grab all reviewers.

    # If someone submits the form.
    if request.method == 'POST':
        # TODO: Validate form and use can_review. & Style review
        review_form = ReviewForm()
        print("Under implementation")
    else:
        review_form = ReviewForm()

    return render(request, 'journal/paper_detail.html',
                  {'section': 'journal', 'paper': paper, 'review_form': review_form, 'reviews': reviews,
                   'can_review': can_review})
