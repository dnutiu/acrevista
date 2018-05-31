import json
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from api import journal
from django.test.client import RequestFactory
from django.core.files import temp as tempfile
from account.models import Profile
from journal.models import Paper, Review


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
        Profile.objects.create(id=0, user=self.test_user)

        # URL's
        self.papers_count = reverse('api:api-papers-count')
        self.papers_submitted = reverse('api:api-papers-submitted')
        self.papers_all = reverse('api:api-papers-all')
        self.papers_editor = reverse('api:api-papers-editor')
        self.papers_no_editor = reverse('api:api-papers-no-editor')
        self.get_token = reverse('api:api-token-login')

        # Authenticate the test user.
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.get_token, data)
        token = response.data["token"]
        self.authorization_header = "JWT {}".format(token)

    def test_get_number_of_papers(self):
        """
            Ensure that the server responds with the correct number of submitted papers.
        """
        response = self.client.get(self.papers_count, None, content_type='application/json')
        self.assertEqual(response.data, 0)

        Paper.objects.create(user=self.test_user)
        response = self.client.get(self.papers_count, None, content_type='application/json')
        self.assertEqual(response.data, 1)

    def test_user_can_get_own_papers(self):
        """
            Ensure than an user can list it's own submitted papers.
        """
        response = self.client.get(self.papers_submitted, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.data, [])

        Paper.objects.create(user=self.test_user)
        response = self.client.get(self.papers_submitted, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)

        # The response will now be an array of order dicts that will have the user pk equal to the test user's.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["user"]["id"], self.test_user.pk)

    def test_user_can_list_all_papers(self):
        """
            Ensure that an admin can list all the papers.
        """
        Paper.objects.create(user=self.test_user)
        Paper.objects.create(user=self.test_user)
        response = self.client.get(self.papers_all, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Make test user a staff member.
        self.test_user.is_staff = True
        self.test_user.save()
        response = self.client.get(self.papers_all, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_can_list_editor_papers(self):
        """
            Ensure than an editor can list papers where he's assigned as an editor.
        """
        Paper.objects.create(user=self.test_user, editor=self.test_user)
        Paper.objects.create(user=self.test_user)
        response = self.client.get(self.papers_editor, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["editor"]["id"], self.test_user.pk)

    def test_user_can_list_no_editor_papers(self):
        """
            Ensure than an editor can list papers where there are any editors assigned.
        """
        Paper.objects.create(user=self.test_user, editor=self.test_user, title="EditorPaper")
        Paper.objects.create(user=self.test_user, title="NoEditorPaper")
        response = self.client.get(self.papers_no_editor, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Make test user a staff member.
        self.test_user.is_staff = True
        self.test_user.save()
        response = self.client.get(self.papers_no_editor, None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "NoEditorPaper")

    def test_user_can_submit_a_paper(self):
        """
            Ensure that an user is able to upload a paper.
        """

        request_factory = RequestFactory()
        manuscript = tempfile.NamedTemporaryFile(suffix=".txt")
        cover_letter = tempfile.NamedTemporaryFile(suffix=".txt")
        manuscript.write(b"This is my stupid paper that required me to research writing this test for over 5h")
        cover_letter.write(b"This is my stupid paper that required me to research writing this test for over 5h")
        manuscript.seek(0)
        cover_letter.seek(0)

        post_data = {
            "title": "My post title",
            "description": "this is my paper description",
            "authors": "no authors",
            "manuscript": manuscript,
            "cover_letter": cover_letter
        }

        request = request_factory.post(self.papers_submitted, HTTP_AUTHORIZATION=self.authorization_header,
                                       data=post_data)

        response = journal.PaperListSubmitted.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_submit_incomplete_paper(self):
        """
            Ensure that an user is not able to upload an incomplete paper.
        """

        request_factory = RequestFactory()
        manuscript = tempfile.NamedTemporaryFile(suffix=".txt")
        manuscript.write(b"This is my stupid paper that required me to research writing this test for over 5h")
        manuscript.seek(0)

        post_data = {
            "title": "My post title",
            "description": "this is my paper description",
            "authors": "no authors",
            "manuscript": manuscript,
        }

        request = request_factory.post(self.papers_submitted, HTTP_AUTHORIZATION=self.authorization_header,
                                       data=post_data)

        response = journal.PaperListSubmitted.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_get_paper_detail(self):
        """
            Ensure that an user can get it's own paper's details, cannot retrieve 404 paper and cannot retrieve
            an admin's paper.
        """
        request_factory = RequestFactory()
        request = request_factory.get(reverse('api:api-paper-detail', kwargs={'pk': 1}),
                                      HTTP_AUTHORIZATION=self.authorization_header)
        Paper.objects.create(user=self.test_user)

        # User can retrieve it's own paper
        response = journal.PaperDetail.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User will get 404 if paper is not found
        response = journal.PaperDetail.as_view()(request, pk=0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # User cannot retrieve paper from staff.
        staff_user = User.objects.create_user('staffuser', 'test@example.com', 'testpassword', is_staff=True)
        Profile.objects.create(user=staff_user)
        Paper.objects.create(user=staff_user)
        response = journal.PaperDetail.as_view()(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Authenticate the staff user & Check if the staff user can retrieve it's own paper
        data = {
            'username': 'staffuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.get_token, data)
        staff_token = "JWT {}".format(response.data["token"])
        request = request_factory.get(reverse('api:api-paper-detail', kwargs={'pk': 1}),
                                      HTTP_AUTHORIZATION=staff_token)
        response = journal.PaperDetail.as_view()(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], staff_user.pk)

        # Staff user can retrieve testuser's paper
        response = journal.PaperDetail.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], self.test_user.pk)

    def test_staff_can_set_editor(self):
        """
            Ensure that a staff user can set itself as an editor to any paper and a regular user can't.
        """
        request_factory = RequestFactory()
        staff_user = User.objects.create_user('staffuser', 'test@example.com', 'testpassword', is_staff=True)
        Profile.objects.create(user=staff_user)
        paper = Paper.objects.create(user=self.test_user)
        Paper.objects.create(user=staff_user)

        # Authenticate the staff user
        data = {
            'username': 'staffuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.get_token, data)
        staff_token = "JWT {}".format(response.data["token"])
        request = request_factory.post(reverse('api:api-papers-editor-add', kwargs={'pk': 1}),
                                       HTTP_AUTHORIZATION=staff_token)

        # Set staff user as an editor on the test user's paper.
        self.assertEqual(paper.editor, None)
        response = journal.set_editor(request, paper.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        paper = Paper.objects.get(user=self.test_user)
        self.assertEqual(paper.editor.pk, staff_user.pk)

        # Staff user can delete itself as an editor
        request = request_factory.delete(reverse('api:api-papers-editor-add', kwargs={'pk': 1}),
                                         HTTP_AUTHORIZATION=staff_token)
        response = journal.set_editor(request, paper.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        paper = Paper.objects.get(user=self.test_user)
        self.assertEqual(paper.editor, None)

        # Non-staff user cannot set itself as an editor
        request = request_factory.delete(reverse('api:api-papers-editor-add', kwargs={'pk': 1}),
                                         HTTP_AUTHORIZATION=self.authorization_header)
        response = journal.set_editor(request, paper.pk)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_add_remove_reviewers(self):
        """
            Ensure that a staff member is able to add and remove reviewers.
        """
        data = {
            "user_pk": self.test_user.pk
        }
        paper = Paper.objects.create(user=self.test_user)

        response = self.client.put(reverse('api:api-papers-reviewer-add', kwargs={'pk': paper.pk}), data=data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_user.is_staff = True
        self.test_user.save()

        response = self.client.put(reverse('api:api-papers-reviewer-add', kwargs={'pk': paper.pk}), data=data,
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(paper.reviewers.last(), self.test_user)

        response = self.client.delete(reverse('api:api-papers-reviewer-add', kwargs={'pk': paper.pk}), data=data,
                                      HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(paper.reviewers.last(), None)

    def test_user_can_list_reviewer_papers(self):
        """
            Ensure than an editor can list papers where he's assigned as a reviewer.
        """
        Paper.objects.create(user=self.test_user, editor=self.test_user).reviewers.add(self.test_user)
        Paper.objects.create(user=self.test_user).reviewers.add(self.test_user)
        Paper.objects.create(user=self.test_user)

        response = self.client.get(reverse('api:api-papers-reviewer'), None, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_can_submit_review(self):
        """
            Ensure that an user can submit a review to a paper on which he's assigned as a reviewer.
            Only one review per user should be submitted for a paper.
        """
        paper = Paper.objects.create(user=self.test_user)
        data = {
            "paper": paper.id,
            "appropriate": "not_appropriate",
            "recommendation": "0",
            "comment": "test"
        }

        # Test user should be able to add a review if he's not assigned as a reviewer.
        response = self.client.post(reverse('api:api-review-add'), json.dumps(data), content_type='application/json',
                                    HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Now he should be able to add the review.
        paper.reviewers.add(self.test_user)
        response = self.client.post(reverse('api:api-review-add'), json.dumps(data), content_type='application/json',
                                    HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(paper.reviews.all()), 1)
        self.assertEqual(response.data['editor_review'], False)

        # Only one review should be submitted
        paper.reviewers.add(self.test_user)
        response = self.client.post(reverse('api:api-review-add'), json.dumps(data), content_type='application/json',
                                    HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_submit_editor_review(self):
        """
            Ensure an editor can submit an editor review.
        """
        paper = Paper.objects.create(user=self.test_user, editor=self.test_user)
        paper.reviewers.add(self.test_user)
        data = {
            "paper": paper.id,
            "appropriate": "not_appropriate",
            "recommendation": "0",
            "comment": "test"
        }
        response = self.client.post(reverse('api:api-review-add'), json.dumps(data), content_type='application/json',
                                    HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(paper.reviews.all()), 1)
        self.assertEqual(response.data['editor_review'], True)

    def test_user_can_get_and_update_review(self):
        """
            Ensure that an user can retrieve and update a review.
        """
        paper = Paper.objects.create(user=self.test_user, editor=self.test_user)
        Review.objects.create(user=self.test_user, paper=paper,
                              appropriate="appropriate", editor_review=True,
                              recommendation="0")
        paper.reviewers.add(self.test_user)
        data = {
            "appropriate": "not_appropriate",
            "recommendation": "+2",
            "comment": "test"
        }

        # User can get review
        response = self.client.get(reverse('api:api-paper-review', kwargs={'pk': paper.id}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User can update review
        response = self.client.put(reverse('api:api-paper-review', kwargs={'pk': paper.id}), data=json.dumps(data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review = Review.objects.all().first()  # Get the only review
        self.assertEqual(review.recommendation, data['recommendation'])

    def test_editor_can_get_list_of_reviews(self):
        """
            Ensure that an editor can get the list of reviews for his paper.
        """
        paper = Paper.objects.create(user=self.test_user)
        response = self.client.get(reverse('api:api-paper-reviews', kwargs={'pk': paper.id}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        # The user is not an editor.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        paper.editor = self.test_user
        paper.save()

        response = self.client.get(reverse('api:api-paper-reviews', kwargs={'pk': paper.id}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_editor_review(self):
        """
            Ensure that an user can get the editor review for the paper if it exists.
        """
        paper = Paper.objects.create(user=self.test_user)
        Review.objects.create(user=self.test_user, paper=paper,
                              appropriate="appropriate", editor_review=False,
                              recommendation="0")

        response = self.client.get(reverse('api:api-paper-reviews-editor', kwargs={'pk': paper.id}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        Review.objects.create(user=self.test_user, paper=paper,
                              appropriate="appropriate", editor_review=True,
                              recommendation="0")
        response = self.client.get(reverse('api:api-paper-reviews-editor', kwargs={'pk': paper.id}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.authorization_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)