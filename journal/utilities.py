from django.contrib.auth.models import User

from journal.models import Paper


def add_reviewer_from_invitation(invitation):
    # Get the paper id from the invitation's name.
    # Get the user from the invitation's email.
    # Pray to god that this is secure.
    paper = Paper.objects.filter(id=int(invitation.name))
    user = User.objects.filter(email=invitation.email)

    if not paper or not user:
        return  # A pai a dat erroare.

    # Get the first result from the query.
    paper = paper[0]
    user = user[0]

    paper.reviewers.add(user)
    paper.save()
