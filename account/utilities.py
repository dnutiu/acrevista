"""
This file will provide various utility functions.
"""
import base64
import os
import datetime
from django.utils import timezone


def generate_security_token(size=32):
    """
    This function will generate a random token that is url safe.
    :param size: The size of the token. Max size is 64 and default size is 32.
    :return: The generated token.
    """
    if size > 64:
        raise ValueError("The maximum size for generate_security_token is 32 bytes!")

    return base64.urlsafe_b64encode(os.urandom(size)).rstrip(b'=').decode('ascii')


def days_from_current_time(days=10):
    """
    Computes a date containing n days from the current time.
    :param days: The number of days.
    :return: The computed date.
    """
    return timezone.now() + datetime.timedelta(days=10)
