from rest_framework import serializers
from .models import Student


class StudentSerialzer(serializers.ModelSerializer) :
    class Meta : 
        read_only_fields = ['id', 'created_at', 'updated_at']
        model = Student
        fields = '__all__'