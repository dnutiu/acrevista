"""acrevista URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from journal import views as journal_views
from . import settings


handler404 = 'account.views.custom_404'
urlpatterns = [
    url(r'^$', journal_views.homepage, name="home"),  # Journal Homepage :)
    url(r'^admin/', admin.site.urls),
    url(r'^journal/', include('journal.urls', namespace='journal', app_name='journal')),
    url(r'^api/', include('api.urls', namespace='api', app_name='api')),
    # Not suitable for production. https://docs.djangoproject.com/en/dev/howto/static-files/deployment/
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^', include('cms.urls')),
]
