from rest_framework import serializers
from .models import Grade

class GradeSerializer(serializers.ModelSerializer) :
    class Meta : 
        read_only_fields = ['id', 'created_at', 'updated_at']
        model = Grade
        fields = '__all__'
        ''''
        [
            'id' , 
            'period' , 
            'module' , 
            'note',
            'status',
            'validated', #or not hmm?
            'ects',
        ]
        '''
        