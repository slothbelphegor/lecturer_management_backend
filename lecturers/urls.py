
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("lecturers", LecturerViewSet, basename="lecturers")
router.register("subjects", SubjectViewSet, basename="subjects")
router.register("evaluations", EvaluationViewSet, basename="evaluations")
router.register("schedules", ScheduleViewSet, basename="schedules")
router.register("recommendations", LecturerRecommendationViewSet, basename="recommendations")
urlpatterns = router.urls
