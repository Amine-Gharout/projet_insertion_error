from django.db import models
import uuid
from program.models import Program
# Create your models here.
class Formation(models.Model) :
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120) 
    program = models.ForeignKey(Program , related_name='formation' , on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta : 
        unique_together = ('name' , 'program')
        ordering = ['created_at']
        verbose_name = 'formation' 
        verbose_name_plural = 'formations' 
        db_table = 'formation'
    
    def __str__(self):
        return f'{self.name}'
        