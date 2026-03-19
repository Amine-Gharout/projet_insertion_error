from rest_framework.routers import DefaultRouter
from .viewset import ModuleViewSet

router = DefaultRouter()
router.register('Module', ModuleViewSet, basename='module')
urlpatterns = router.urls