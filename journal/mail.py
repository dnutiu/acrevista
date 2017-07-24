from django.contrib.auth.models import User
from acrevista.settings import EMAIL_NOREPLY
from django.core.mail import send_mail


def get_staff_members():
    staff_members = User.objects.filter(is_staff=True)
    recipients = []

    for member in staff_members:  # Every staff member should have a valid email.
        if member.email:
            recipients.append(member.email)
    return recipients


def send_mail_to_staff(paper_title, authors):
    """
    Notifies all the staff members (editors) that a new paper has been submitted.
    :param paper_title: The title of the paper that will appear in the mail.
    :param authors: Tuple containing the authors of the paper.
    """
    # Fixme: Perhaps make this async
    # Send mail to everyone from the staff. Perhaps run async idk?
    recipients = get_staff_members()

    message = "A new paper: '{}' has been submitted by the following authors:" \
              "\n(First Name, Last Name, Email, Affiliation, Country \n{}".format(paper_title, authors)
    subject = "A new paper has been submitted!"

    send_mail(subject, message, EMAIL_NOREPLY, recipients, fail_silently=True)


def send_mail_new_review(paper_title, recipient):
    """
    Notifies the user that a new review has been added.
    :param recipient: The recipient that will be notified.
    :param paper_title: The title of the paper
    """
    subject = "New review: {}".format(paper_title)
    message = "A new review for the paper {} has been added!".format(paper_title)
    send_mail(subject, message, EMAIL_NOREPLY, (recipient,), fail_silently=False)


#https://stackoverflow.com/questions/1160019/django-send-email-on-model-change
def send_mail_paper_status_update(paper_title, old_status, new_status):
    recipients = get_staff_members()
    subject = "{} - Status was changed.".format(paper_title)
    message = "The status for {} was change from {} to {}.".format(paper_title, old_status, new_status)
    send_mail(subject, message, EMAIL_NOREPLY, recipients, fail_silently=True)
