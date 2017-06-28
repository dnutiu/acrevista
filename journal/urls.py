from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name="journal_home"),
    url(r'^submit/', views.submit_paper, name="journal_submit"),
]