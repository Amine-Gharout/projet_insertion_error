from rest_framework.routers import DefaultRouter
from .models import Program
from .viewset import ProgramViewSet

router = DefaultRouter()
router.register(r'Program', ProgramViewSet, basename='program')
urlpatterns = router.urls