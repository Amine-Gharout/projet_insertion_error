from django.db import models
from module.models import Module
from formation.models import Formation
import uuid


# Create your models here.
class Curriculum_module(models.Model) :
    
    class Year(models.TextChoices) :
        YEAR_1 = '1CP' , '1st Year Preparatory'
        YEAR_2 = '2CP' , '2nd Year Preparatory'
        YEAR_3 = '1CS' , '1st Year Higher cycle'
        YEAR_4 = '2CS' , '2nd Year Higher cycle'
        YEAR_5 = '3CS' , '3rd Year Higher cycle'
        YEAR_6 = 'L1' , '1st Year License'
        YEAR_7 = 'L2' , '2nd Year License'
        YEAR_8 = 'L3' , '3rd Year License'
        YEAR_9 = 'M1' , '1st Year Master'
        YEAR_10 = 'M2' , '2nd Year Master'
        YEAR_11 = 'D' , 'Doctorate'
        
    class Semester(models.IntegerChoices) :
        SEMESTER_1 = 1 , 'Semester 1'
        SEMESTER_2 = 2 , 'Semester 2'
    
    id = models.UUIDField(primary_key=True , default=uuid.uuid4, editable=False) 
    module = models.ForeignKey(Module , related_name='curriculum_modules' ,on_delete=models.CASCADE)
    coefficient = models.IntegerField() 
    formation = models.ForeignKey(Formation, related_name='curriculum_modules', on_delete=models.CASCADE)   
    NE = models.FloatField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True , choices=Semester.choices)
    year = models.CharField(max_length=20, null=True, blank=True , choices=Year.choices)
    code = models.CharField(max_length=100, null=True, blank=True ) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        unique_together = ('module', 'formation', 'semester', 'year')
        ordering = ['formation', 'module' , 'coefficient' , 'created_at' , 'semester' , 'year' , 'NE']
        verbose_name = 'curriculum module' 
        verbose_name_plural = 'curriculum modules' 
        db_table = 'curriculum_module' 
    
    def __str__(self):
        return f'{self.formation} {self.module} {self.coefficient} {self.semester} {self.year} {self.NE}'