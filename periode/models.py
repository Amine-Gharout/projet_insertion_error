from django.db import models
from curriculum.models import Curriculum
import uuid
# Create your models here.

class Periode(models.Model) :
    id = models.UUIDField(primary_key=True , default=uuid.uuid4, editable=False) 
    name = models.CharField(max_length=100)
    curriculum = models.ForeignKey(Curriculum , related_name='periodes' , on_delete=models.CASCADE)
    credits = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    moyenne = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        ordering = ['curriculum', 'rank']
        verbose_name = 'Periode' 
        verbose_name_plural = 'Periodes'
        db_table = 'periode'
        
    def __str__(self):
        return f'{self.curriculum} - {self.name} ({self.credits} credits)'
