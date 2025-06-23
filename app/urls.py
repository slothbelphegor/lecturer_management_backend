"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import path, include, re_path
from knox import views as knox_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('users.urls')),
    # path('' , include('lecturers.urls')),
    # path('', include('documents.urls')),
    
    # # Authentication paths from Knox
    # # path('api/auth/', include('knox.urls')),
    # path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    # path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    # # Password reset authentication paths
    # path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
    # # Catch-all: serve React index.html for any other route
    # re_path(r'^(?!admin/|api/|static/|media/).*$',
    #     TemplateView.as_view(template_name="index.html"), name='react'),
    re_path(r'^.*$', TemplateView.as_view(template_name="index.html")),
]
