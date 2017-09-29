"""
    Adapted from the ol' http://www.ac.upt.ro/journal/

"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SubmitPaperForm, ReviewForm
from .validators import validate_authors
from django.http import Http404
from .models import Paper
from .mail import send_mail_to_staff, send_mail_new_review


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

            send_mail_to_staff(paper.title, paper.authors)

            return render(request, "journal/submit_done.html", {'section': 'journal', 'paper': paper})
        else:
            messages.warning(request, "Error submitting paper!")
    else:
        form = SubmitPaperForm()
    return render(request, "journal/submit.html", {'section': 'journal', 'form': form})


def guidelines(request):
    return render(request, 'journal/guidelines.html', {'section': 'journal'})


def profile(request):
    return render(request, 'journal/profile.html', {'section': 'journal'})


def history(request):
    return render(request, 'journal/history.html', {'section': 'journal'})


def review(request):
    return render(request, 'journal/review.html', {'section': 'journal'})


@login_required
def paper_review(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    can_review = request.user in paper.reviewers.all()

    # Raise 404 if we're looking at someone's else paper and we're not the author or reviewers
    if not can_review and request.user != paper.user:
        raise Http404

    # If someone submits the form.
    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST, files=request.FILES)
        if review_form.is_valid() and can_review:
            new_review = review_form.save(commit=False)
            new_review.user = request.user
            new_review.paper = paper
            new_review.save()
            messages.success(request, "Review posted!")
            # Redirects automatically to paper detail.

            # Notify editor or user that a new review has been added.
            if new_review.editor_review:
                if paper.user:
                    send_mail_new_review(paper.title, paper.user.email)
            else:
                if paper.editor:
                    send_mail_new_review(paper.title, paper.editor.email)

            return redirect(paper)
        else:
            messages.warning(request, "Error submitting review.")
    else:
        review_form = ReviewForm()

    return render(request, 'journal/paper_review.html',
                  {'section': 'journal', 'paper': paper, 'review_form': review_form})


@login_required
def paper_detail(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    can_review = request.user in paper.reviewers.all()

    # Raise 404 if we're looking at someone's else paper and we're not the author or reviewers
    if not can_review and request.user != paper.user:
        raise Http404

    reviews = paper.reviews.all()  # Grab all reviewers.

    return render(request, 'journal/paper_detail.html',
                  {'section': 'journal', 'paper': paper, 'reviews': reviews, 'can_review': can_review})
