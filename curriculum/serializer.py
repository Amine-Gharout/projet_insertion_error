from rest_framework import serializers
from .models import Curriculum

class CurriculumSerializer(serializers.ModelSerializer) :
    class Meta :
        read_only_fields = ['id', 'created_at', 'updated_at']
        model = Curriculum
        fields = '__all__' 