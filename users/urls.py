from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('register', RegisterViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')
router.register('users', UserViewSet, basename='users')
router.register("groups",GroupViewSet, basename="groups")
urlpatterns = router.urls
