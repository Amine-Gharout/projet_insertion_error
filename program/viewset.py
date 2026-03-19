from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Program
from .serializer import ProgramSerializer
from django_filters.rest_framework import DjangoFilterBackend


class ProgramViewSet(viewsets.ModelViewSet) :
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend]
    search_fields = ['title',  'description']
    ordering_fields = ['title', 'code' , 'description', 'cycle', 'diploma', 'created_at']
    ordering = ['title']
    filterset_fields = ['cycle', 'diploma' , 'speciality' , 'code']