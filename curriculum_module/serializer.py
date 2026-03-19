from rest_framework import serializers 
from .models import Curriculum_module

class Curricul_Module_Serializer(serializers.ModelSerializer):
    coefficient = serializers.IntegerField(min_value=1, max_value=10)
    
    class Meta:
        model = Curriculum_module
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']  # ← removed 'formation' and 'module'