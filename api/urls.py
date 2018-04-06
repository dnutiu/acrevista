from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from api.account import UserCreate, TestPermissions, ChangePasswordView, ChangeNameView
from api.profile import ProfileDetail, valid_titles, valid_countries

urlpatterns = [
    # Account
    url(r'^token-verify/', verify_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token, name="api-token-refresh"),
    url(r'^token-auth/$', obtain_jwt_token, name="api-token-login"),
    url(r'^register/$', UserCreate.as_view(), name="api-register"),
    url(r'^change-password/$', ChangePasswordView.as_view(), name="api-change-password"),
    url(r'^change-user-details/$', ChangeNameView.as_view(), name="api-change-user-details"),
    # Profile
    url(r'^profile/valid_titles/$', valid_titles, name="api-profile-valid-titles"),
    url(r'^profile/valid_countries/$', valid_countries, name="api-profile-valid-counties"),
    url(r'^profile/(?P<pk>[0-9]+)/$', ProfileDetail.as_view(), name="api-get-profile"),
    # Test
    url(r'^prajituri/$', TestPermissions.as_view(), name="api-test-protected"),
]
