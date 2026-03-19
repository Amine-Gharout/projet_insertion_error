from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
# from django_filters.rest_framework import DjangoFilterBackend
from .models import Module
from .serializer import ModuleSerializer
from django_filters.rest_framework import DjangoFilterBackend


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    filterset_fields = ['code']
    
