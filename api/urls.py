from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from api.account import UserCreate, TestPermissions, ChangePasswordView, ChangeNameView
from api.journal import papers_count, PaperListSubmitted, PaperListAll, PaperListEditor, PaperListNoEditor, PaperDetail, \
    set_editor, AddRemoveReviewer, PaperListReviewer
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
    # Journal
    url(r'^papers/count/$', papers_count, name="api-papers-count"),
    url(r'^papers/all/$', PaperListAll.as_view(), name="api-papers-all"),
    url(r'^papers/editor/$', PaperListEditor.as_view(), name="api-papers-editor"),
    url(r'^papers/reviewer/$', PaperListReviewer.as_view(), name="api-papers-reviewer"),
    url(r'^papers/editor/(?P<pk>[0-9]+)/$', set_editor, name="api-papers-editor-add"),
    url(r'^papers/reviewer/(?P<pk>[0-9]+)/$', AddRemoveReviewer.as_view(), name="api-papers-reviewer-add"),
    url(r'^papers/no-editor/$', PaperListNoEditor.as_view(), name="api-papers-no-editor"),
    url(r'^papers/detail/(?P<pk>[0-9]+)/$', PaperDetail.as_view(), name="api-paper-detail"),
    url(r'^papers/$', PaperListSubmitted.as_view(), name="api-papers-submitted"),

    # Test
    url(r'^prajituri/$', TestPermissions.as_view(), name="api-test-protected"),
]
