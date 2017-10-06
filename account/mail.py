"""
This file will implement useful methods for sending emails from withing this package.
"""
from acrevista.settings import EMAIL_NOREPLY, BASE_URL, SITE_NAME
from django.core.mail import send_mail


def send_token_email(recipient, token):
    """
    This function notifies the user that a token has been generated for him.
    """
    # TODO: Maybe add who requested the review.
    # TODO: Find a better way to generate the url.
    url = "{}/account/login?token={}".format(BASE_URL, token)
    subject = "Review requested!"
    message = '''
    Hello,
    
    Somebody at {site_name}, requested that you may review a paper.
    
    Please click <a href="{url}">here</a> to learn more.
    
    Sincerely,
    The {site_name} team!
    
    '''.format(site_name=SITE_NAME, url=url)
    send_mail(subject, message, EMAIL_NOREPLY, (recipient,), fail_silently=False)
