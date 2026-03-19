from django.db import models
import uuid

# Create your models here.
class Module(models.Model) : 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True , blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    
    class Meta :
        ordering = ['name'] 
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        db_table = 'module'
        
    def __str__(self) :
        return f"{self.name} ({self.code})"
    
