from django.db import models
import uuid

# Create your models here.

class Program(models.Model) : 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100 , unique=True)
    code = models.CharField(max_length=20 , unique=True , blank=True , null=True)
    description = models.TextField(blank=True , null=True)
    cycle = models.CharField(max_length=20 , null=True , blank=True)
    diploma = models.CharField(max_length=50 , null=True , blank=True)
    speciality = models.CharField(max_length=50 , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta : 
        ordering = ['title']
        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'
        db_table = 'program'
        
    def __str__(self):
        return f'{self.title} ({self.code}) - {self.cycle} - {self.diploma} - {self.speciality}'
