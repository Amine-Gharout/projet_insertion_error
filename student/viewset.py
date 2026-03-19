from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializer import StudentSerialzer
from django_filters.rest_framework import DjangoFilterBackend


class StudentViewSet(viewsets.ModelViewSet) :
    queryset = Student.objects.all()
    serializer_class = StudentSerialzer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['matricule', 'first_name', 'last_name', 'birth_date', 'created_at']
    filterset_fields = ['matricule', 'sexe' , 'first_name', 'last_name']
    ordering = ['first_name', 'last_name']  
    
    