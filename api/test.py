import json
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status

from account.models import Profile
from journal.models import Paper


class AccountsTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Profile.objects.create(user=self.test_user)

        # URL's
        self.create_url = reverse('api:api-register')
        self.get_token = reverse('api:api-token-login')
        self.sample_protected_endpoint = reverse('api:api-test-protected')
        self.change_details = reverse('api:api-change-user-details')
        self.change_password = reverse('api:api-change-password')

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

    def test_user_can_change_password(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.get_token, data)
        token = response.data["token"]

        data = {
            "old_password": "testpassword",
            "new_password": "testpassword1"
        }
        response = self.client.put(self.change_password, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_change_name(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.get_token, data)
        token = response.data["token"]

        data = {
            "first_name": "Dr",
            "last_name": "Phd"
        }
        response = self.client.put(self.change_details, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfileTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.staff_user = User.objects.create_user('staffuser', 'test@example.com', 'testpassword', is_staff=True)

        # Create the profiles
        Profile.objects.create(user=self.test_user)
        Profile.objects.create(user=self.staff_user)

        # URL's
        self.get_token_url = reverse('api:api-token-login')
        self.get_user_profile = reverse('api:api-get-profile', kwargs={'pk': self.test_user.profile.pk})
        self.get_staff_profile = reverse('api:api-get-profile', kwargs={'pk': self.staff_user.profile.pk})
        self.get_valid_titles = reverse('api:api-profile-valid-titles')
        self.get_valid_countries = reverse('api:api-profile-valid-counties')

        # Get testuser's token
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        self.test_user_token = self.get_token(data)

    def get_token(self, data):
        response = self.client.post(self.get_token_url, data)
        return response.data["token"]

    def test_user_can_get_own_profile(self):
        # Get own profile
        response = self.client.get(self.get_user_profile, {}, content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Default country is Romania
        self.assertEqual(response.data['country'], "Romania")

    def admin_can_get_any_profile(self):
        data = {
            'username': 'staffuser',
            'password': 'testpassword',
        }
        token = self.get_token(data)

        # Get test user profile
        response = self.client.get(self.get_user_profile, data, content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get admin user profile
        response = self.client.get(self.get_staff_profile, data, content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_get_any_profile(self):
        # Get admin user profile
        response = self.client.get(self.get_staff_profile, {}, content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anon_user_cant_get_profile(self):
        response = self.client.get(self.get_user_profile, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_update_profile(self):
        data = {
            "title": "Dr",
            "phone": "777-7777-7777",
            "country": "Ukraine",
            "affiliation": "University1"
        }
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['phone'], data['phone'])
        self.assertEqual(response.data['country'], data['country'])
        self.assertEqual(response.data['affiliation'], data['affiliation'])

    def test_user_can_update_profile_title(self):
        data = {
            "title": "Dr",
        }
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])

        # Invalid title
        data["title"] = "Master"
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_update_profile_country(self):
        data = {
            "country": "Ukraine",
        }
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country'], data['country'])

        # Invalid country
        data["country"] = "America"
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_update_profile_phone(self):
        data = {
            "phone": "777-7777-7777",
        }
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], data['phone'])

    def test_user_can_update_profile_affiliation(self):
        data = {
            "affiliation": "University1"
        }
        response = self.client.put(self.get_user_profile, json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION="JWT {}".format(self.test_user_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['affiliation'], data['affiliation'])

    def test_get_valid_titles(self):
        response = self.client.get(self.get_valid_titles, None, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_countries(self):
        response = self.client.get(self.get_valid_countries, None, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaperTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Profile.objects.create(user=self.test_user)

        # URL's
        self.papers_count = reverse('api:api-papers-count')

    def test_get_number_of_papers(self):
        """
            Ensure that the server responds with the correct number of submitted papers.
        """
        response = self.client.get(self.papers_count, None, content_type='application/json')
        self.assertEqual(response.data, 0)

        Paper(user=self.test_user).save()
        response = self.client.get(self.papers_count, None, content_type='application/json')
        self.assertEqual(response.data, 1)
