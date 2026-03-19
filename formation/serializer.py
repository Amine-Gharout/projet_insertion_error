from rest_framework import serializers
from .models import Formation

class FormationSerilizer(serializers.ModelSerializer) :
    class Meta : 
        model = Formation 
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']