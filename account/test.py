from django.contrib.auth.models import User
from django.test import TestCase
from .models import LoginToken
from django.utils import timezone
import datetime


class LoginTokenTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testing@testing.com", email="testing@testing.com")
        self.lt = LoginToken(user=self.user)

    def test_login_token_created(self):
        # print("test_login_token_created:", self.lt.user, self.lt.token, self.lt.expiry_date)
        self.assertTrue(self.lt,
                        "LoginToken was created. {} {} {}".format(self.lt.user, self.lt.token, self.lt.expiry_date))

    def test_login_token_is_expired(self):
        expired_time = timezone.now() + datetime.timedelta(days=50)
        self.assertTrue(expired_time > self.lt.expiry_date, "LoginToken is expired after 10 days.")

    def test_login_token_not_expired(self):
        time = timezone.now()
        self.assertTrue(time < self.lt.expiry_date, "LoginToken is not expired.")

    def test_token_is_greater_than_32_bytes(self):
        print(len(self.lt.token))
        self.assertTrue(len(self.lt.token) > 32, "LoginToken has a length of 32 bytes.")
