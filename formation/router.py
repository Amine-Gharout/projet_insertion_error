from rest_framework.routers import DefaultRouter 
from .viewset import FormationViewSet

router = DefaultRouter()
router.register('Formation' ,FormationViewSet , basename='formation')
urlpatterns = router.urls