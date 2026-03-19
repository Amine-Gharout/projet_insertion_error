from rest_framework.routers import DefaultRouter
from .viewset import StudentViewSet

router = DefaultRouter()
router.register('Student',StudentViewSet , basename='student')

urlpatterns = router.urls