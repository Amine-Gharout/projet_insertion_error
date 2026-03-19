from rest_framework.routers import DefaultRouter
from .viewset import Curricul_Module_Viewset

router = DefaultRouter()
router.register('CurriculumModule', Curricul_Module_Viewset , basename='curriculum-module')
urlpatterns = router.urls