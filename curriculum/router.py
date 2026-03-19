from rest_framework.routers import DefaultRouter
from .viewset import CurriculumViewSet
router = DefaultRouter()
router.register('Curriculum', CurriculumViewSet, basename='curriculum')
urlpatterns = router.urls
