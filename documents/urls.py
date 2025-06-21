from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="documents")

urlpatterns = router.urls