from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from api.account import UserCreate

urlpatterns = [
    url(r'^login/$', obtain_jwt_token, name="api-login"),
    url(r'^register/$', UserCreate.as_view(), name="api-register"),
]
