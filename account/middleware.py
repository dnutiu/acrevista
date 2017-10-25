# Login the user automatically using the LoginToken
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from account.models import LoginToken


class LoginTokenMiddleware(object):
    """
    Checks for LoginToken on every's user request and if the Token is valid,
    it logs the user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.GET.get('token', None)
        if token:
            login_token = LoginToken.objects.filter(token=token)
            if not login_token:  # We don't have any tokens in database.
                messages.warning(request, "Invalid login token!")
            else:
                # Check if the token is still valid
                if login_token[0].expiry_date < timezone.now():
                    messages.warning(request, "Token is expired!")
                else:
                    # The login token is still valid, login the user!
                    messages.success(request, "You have been logged in successfully as {}!"
                                     .format(str(login_token[0].user)))
                    login(request, login_token[0].user)

        response = self.get_response(request)

        return response
