from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend
from .models import Grade
from .serializer import GradeSerializer
from django_filters.rest_framework import DjangoFilterBackend

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend]
    search_fields = ['period__name','module__module__name' , 'period__curriculum__student__first_name', 'period__curriculum__student__last_name']
    ordering_fields =  ['period__name','module__module__name','note']
    ordering = ['note']
    filterset_fields = {
        'note': ['exact', 'gte', 'lte'],
        'status': ['exact'],
        'source': ['exact'],
        'validated': ['exact'],
        'ects': ['exact', 'gte', 'lte'],
        'period__curriculum__student__matricule': ['exact'],
        'period': ['exact'],
        'module': ['exact'],
        'module__module': ['exact'],
    }
    
