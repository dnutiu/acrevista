from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name="journal_home"),
    url(r'^submit/$', views.submit_paper, name="journal_submit"),
    url(r'^history/$', views.history, name="journal_history"),
    url(r'^profile/$', views.profile, name="journal_profile"),
    url(r'^review/$', views.review, name="journal_review"),
    url(r'^paper/(?P<paper_id>\d+)/detail$', views.paper_detail, name="paper_detail"),
]
