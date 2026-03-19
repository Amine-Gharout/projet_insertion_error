from rest_framework.routers import DefaultRouter
from .viewset import GradeViewSet

router = DefaultRouter()
router.register('Grade', GradeViewSet, basename='grade')
urlpatterns = router.urls