"""site02 URL Configuration

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
from django.conf.urls import url
from django.contrib import admin

import main.views

from django.contrib.auth.views import login, logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hot/$', main.views.hot),
    url(r'^dashboard/$', main.views.dashboard),
    url(r'^related_words/$', main.views.related_words),
    url(r'^related_words/data\.json', main.views.related_words_data),
    url(r'^leader/$', main.views.leader),
    url(r'^leader/data\.json', main.views.leader_data),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout),
    url(r'$', login),
]
