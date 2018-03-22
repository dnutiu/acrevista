from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from api.account import UserCreate, TestPermissions

urlpatterns = [
    url(r'^token-verify/', verify_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token, name="api-token-refresh"),
    url(r'^token-auth/$', obtain_jwt_token, name="api-token-login"),
    url(r'^register/$', UserCreate.as_view(), name="api-register"),
    url(r'^prajituri/$', TestPermissions.as_view(), name="api-test-protected"),
]
