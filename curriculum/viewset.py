from rest_framework import viewsets
from .models import Curriculum
from .serializer import CurriculumSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
class CurriculumViewSet(viewsets.ModelViewSet) :
    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['student__first_name', 'student__last_name', 'formation__name','formation__program__title','formation__program__description']
    ordering_fields = ['moyenne_finale', 'moyenne_concours', 'moyenne_rachat', 'rank']
    ordering = ['-moyenne_finale']
    filterset_fields = {
        'moyenne_finale': ['exact', 'gte', 'lte'],
        'moyenne_concours': ['exact', 'gte', 'lte'],
        'moyenne_rachat': ['exact', 'gte', 'lte'],
        'rank': ['exact', 'gte', 'lte'],
        'student' : ['exact'],
        'formation' : ['exact'],
        'status' : ['exact'],
        'student__matricule': ['exact'],
        'section' : ['exact'],
        'group' : ['exact'],
    }
    