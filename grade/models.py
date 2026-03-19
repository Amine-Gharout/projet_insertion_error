from django.db import models
import uuid
from curriculum_module.models import Curriculum_module
from periode.models import Periode 

# Create your models here.
class Grade(models.Model) : 
    
    class GradeTYPE(models.TextChoices) :
        NORMAL = 'NORMAL', 'GRADE NORMAL'
        RATTRAPAGE  = 'RATTR', 'GRADE RATTRAPAGE'
        RACHA = 'RACHA', 'GRADE RACHAT'
        CONCOURS = 'CONCOURS', 'GRADE CONCOURS'
        
    class GradeSource(models.TextChoices) :
        OCR = 'OCR', 'OCR'
        MANUAL = 'MANUAL', 'MANUAL'  
        IMPORT = 'IMPORT', 'IMPORT'
        
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    period = models.ForeignKey(Periode, on_delete=models.CASCADE, related_name="grades")
    module = models.ForeignKey(Curriculum_module ,on_delete=models.CASCADE,related_name="grades")
    note = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status= models.CharField(null=True, blank=True , choices=GradeTYPE.choices , max_length=20)
    source = models.CharField(null=True, blank=True , choices=GradeSource.choices , max_length=20)
    validated = models.BooleanField(default=False)
    ects = models.CharField(null=True , blank=True , max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta :
        unique_together = ('period', 'module')
        ordering = ['period__name', 'module__module__name','status','note'] 
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        db_table = 'grade'
        
    def __str__(self) :
        return f"module: {self.module.module.name} | note: {self.note} | decision: {self.status}"
    
