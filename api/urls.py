"""
    This file defines the URL's for the API.
"""
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from api import account
from api import journal
from api.profile import ProfileDetailView, valid_titles, valid_countries

urlpatterns = [
    # Account
    url(r'^token-verify/', verify_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token, name="api-token-refresh"),
    url(r'^token-auth/$', obtain_jwt_token, name="api-token-login"),
    url(r'^register/$', account.UserCreateView.as_view(), name="api-register"),
    url(r'^change-password/$', account.ChangePasswordView.as_view(), name="api-change-password"),
    url(r'^change-user-details/$', account.ChangeNameView.as_view(), name="api-change-user-details"),
    url(r'^account/users/$', account.UserListView.as_view(), name="api-list-users"),
    # Profile
    url(r'^profile/valid_titles/$', valid_titles, name="api-profile-valid-titles"),
    url(r'^profile/valid_countries/$', valid_countries, name="api-profile-valid-counties"),
    url(r'^profile/(?P<pk>[0-9]+)/$', ProfileDetailView.as_view(), name="api-get-profile"),
    # Journal
    url(r'^papers/count/$', journal.papers_count, name="api-papers-count"),
    url(r'^papers/all/$', journal.PaperListAllView.as_view(), name="api-papers-all"),
    url(r'^papers/editor/$', journal.PaperListEditorView.as_view(), name="api-papers-editor"),
    url(r'^papers/editor/self$', journal.PaperListEditorSelfView.as_view(), name="api-papers-editor-self"),
    url(r'^papers/reviewer/$', journal.PaperListReviewerView.as_view(), name="api-papers-reviewer"),
    url(r'^papers/(?P<pk>[0-9]+)/editor/$', journal.set_editor, name="api-papers-editor-add"),
    url(r'^papers/(?P<pk>[0-9]+)/reviewer/$', journal.AddRemoveReviewerView.as_view(), name="api-papers-reviewer-add"),
    url(r'^papers/no-editor/$', journal.PaperListNoEditorView.as_view(), name="api-papers-no-editor"),
    url(r'^papers/(?P<pk>[0-9]+)/detail/$', journal.PaperDetailView.as_view(), name="api-paper-detail"),
    url(r'^papers/(?P<pk>[0-9]+)/review/$', journal.ReviewRetrieveUpdateView.as_view(), name="api-paper-review"),
    url(r'^papers/(?P<pk>[0-9]+)/reviews/$', journal.ReviewListView.as_view(), name="api-paper-reviews"),
    url(r'^papers/(?P<pk>[0-9]+)/reviews/editor/$', journal.EditorReviewView.as_view(),
        name="api-paper-reviews-editor"),
    url(r'^papers/$', journal.PaperListSubmittedView.as_view(), name="api-papers-submitted"),
    url(r'^review/$', journal.ReviewAddView.as_view(), name="api-review-add"),

    # Test
    url(r'^prajituri/$', account.TestPermissionsView.as_view(), name="api-test-protected"),
]
