from django.contrib.auth.models import User

from journal.models import Paper


def add_reviewer_from_invitation(invitation):
    # Get the paper id from the invitation's name.
    # Get the user from the invitation's email.
    # Pray to god that this is secure.
    return add_reviewer(invitation.email, int(invitation.name))

def add_reviewer(email, paper_id):
    paper = Paper.objects.filter(id=paper_id)
    user = User.objects.filter(email=email)

    if not paper or not user:
        return False

    # Get the first result from the query.
    paper = paper[0]
    user = user[0]

    paper.reviewers.add(user)
    paper.save()

    return True