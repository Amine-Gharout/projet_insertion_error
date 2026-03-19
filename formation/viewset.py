from rest_framework import viewsets
from rest_framework.filters import OrderingFilter , SearchFilter
from .serializer import FormationSerilizer
from .models import Formation
from django_filters.rest_framework import DjangoFilterBackend

class FormationViewSet(viewsets.ModelViewSet) : 
    queryset = Formation.objects.all() 
    serializer_class = FormationSerilizer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend]
    search_fields = ['name' , 'program__title' , 'program__description' , 'program__code']
    ordering_fields = ['name' , 'created_at' , 'updated_at']
    ordering = ['created_at']
    filterset_fields = ['program__code' , 'program' , 'program__cycle' , 'program__diploma' , 'program__speciality']
    