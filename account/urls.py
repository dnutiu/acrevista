from django.conf.urls import url
from django.contrib.auth.views import (logout, logout_then_login, password_change, password_change_done,
                                       password_reset, password_reset_done, password_reset_confirm,
                                       password_reset_complete)
from . import views

urlpatterns = [
    # login / logout urls
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^logout-then-login/$', logout_then_login, name='logout_then_login'),
    # Password change.
    url(r'^password-change/$', password_change, name='password_change'),
    url(r'^password-change/done/$', password_change_done, name='password_change_done'),
    # restore password urls
    url(r'^password-reset/$', password_reset, name='password_reset'),
    url(r'^password-reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^password-reset/complete/$', password_reset_complete, name='password_reset_complete'),
    # Account url
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^email-change/$', views.change_email, name='email_change'),
    url(r'^personal-details/$', views.change_personal_details, name='personal_details'),
    # url(r'^generate-token/$', views.generate_user_token, name='generate_token'),
    url(r'^invite/(?P<rev_id>[\w\d]+)/accept', views.accept_invite, name="accept_invite"),
    url(r'^invite/(?P<rev_id>[\w\d]+)/reject', views.reject_invite, name="reject_invite"),
    url(r'^invite/', views.invite_user, name="invite_user"),
    url(r'^get-invite/$', views.get_invitations, name="get_invite"),
    url(r'^cancel-invite/$', views.cancel_invitation, name="cancel_invite")
    # url(r'^users/$', views.user_list, name='user_list'),
    # # Must be placed BEFORE the users/username url
    # url(r'^users/follow/$', views.user_follow, name='user_follow'),
    # # name=user_detail is used for get_ab_solute url in settings.py
    # url(r'^users/(?P<username>[-\w]+)/$', views.user_detail, name='user_detail'),
]
