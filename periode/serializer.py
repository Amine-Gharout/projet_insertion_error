from rest_framework import serializers
from .models import Periode

class PeriodeSerializer(serializers.ModelSerializer) :
    class Meta :
        read_only_fields = ['id', 'created_at', 'updated_at']
        model = Periode
        fields = '__all__'