from rest_framework import viewsets 
from .models import Periode
from .serializer import PeriodeSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
class PeriodeViewset(viewsets.ModelViewSet) :
    queryset = Periode.objects.all()
    serializer_class = PeriodeSerializer
    filter_backends = [SearchFilter, OrderingFilter , DjangoFilterBackend]
    search_fields = ['name', 'curriculum__student__first_name', 'curriculum__student__last_name','curriculum__formation__name','curriculum__formation__program__title' , 'curriculum__formation__program__description']
    ordering_fields = ['rank', 'credits','created_at', 'updated_at' , 'moyenne']
    ordering = ['rank']
    filterset_fields = {'curriculum__student__matricule': ['exact'],
                        'credits': ['exact', 'gte', 'lte'],
                        'rank': ['gte', 'lte' , 'exact'],
                        'moyenne': ['gte', 'lte' , 'exact']  , 
                        'curriculum' : ['exact']  , 
                        }
    
