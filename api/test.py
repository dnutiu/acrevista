from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status


class AccountsTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')

        # URL's
        self.create_url = reverse('api:api-register')
        self.get_token = reverse('api:api-token-login')
        self.sample_protected_endpoint = reverse('api:api-test-protected')

    def test_protected_endpoint(self):
        """
        Ensure that an anonymous user can't access a protected endpoint and a logged in user can.
        """
        response = self.client.get(self.sample_protected_endpoint, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Create user
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'foobar@example.com',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get token
        response = self.client.post(self.get_token, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["token"]

        # Auth
        response = self.client.get(self.sample_protected_endpoint, data, content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Da")

    def test_user_can_login_via_token(self):
        """
        Ensure that the user can login via token after it was created.
        If the user has
        """
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'foobar@example.com',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

        response = self.client.post(self.get_token, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data['password'] = "ha"
        response = self.client.post(self.get_token, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['email'], data['email'])
        self.assertFalse('password' in response.data)

    def test_create_user_with_short_password(self):
        """
        Ensures user is not created for password lengths less than 8.
        """

        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': 'foo'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_no_password(self):
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': ''
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['password']), 1)

    def test_create_user_with_preexisting_email(self):
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'testuser'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_invalid_email(self):
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'foobarbaz',
            'email': 'testing',
            'passsword': 'foobarbaz'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)

    def test_create_user_with_no_email(self):
        data = {
            'first_name': "Bakir",
            'last_name': 'aos',
            'username': 'foobar',
            'email': '',
            'password': 'foobarbaz'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
