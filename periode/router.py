from rest_framework.routers import DefaultRouter
from .viewset import PeriodeViewset

router = DefaultRouter()
router.register('Periode', PeriodeViewset, basename='periode')
urlpatterns = router.urls