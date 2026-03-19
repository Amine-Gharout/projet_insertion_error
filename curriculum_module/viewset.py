from rest_framework import viewsets
from .models import Curriculum_module
from .serializer import Curricul_Module_Serializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend



class Curricul_Module_Viewset(viewsets.ModelViewSet) :
    queryset = Curriculum_module.objects.all()
    serializer_class = Curricul_Module_Serializer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend] 
    search_fields = ['module__name', 'formation__name', 'module__description' ]    
    ordering_fields = ['module__name', 'formation__name', 'coefficient', 'NE', 'semester', 'year'  , 'created_at']
    ordering = ['module__name' ]
    filterset_fields = {
        'semester': ['exact'],
        'year': ['exact'],
        'NE': ['exact' , 'gte', 'lte'],  # range support
        'coefficient': ['exact', 'gte', 'lte'],  # range support
        'formation': ['exact'],
        'module': ['exact'],
    }
