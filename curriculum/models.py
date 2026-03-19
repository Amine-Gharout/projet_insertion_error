from django.db import models
import uuid
from student.models import Student
from formation.models import Formation

# Create your models here.
class Curriculum(models.Model) :
    
    class Status(models.TextChoices) :
        ADMITTED   = 'ADMIS' , 'Admis'
        REPEATER   = 'INSCRIT' , 'Inscrit'
        EXCLUDED   = 'EXCLU' , 'Exclu'
        RACHAT     = 'RACHAT' , 'Admis avec rachat'
        RATTRAPAGE = 'RATTRAPAGE' , 'Admis en rattrapage'
        
        
    id = models.UUIDField(primary_key=True , default=uuid.uuid4 , editable=False)
    section = models.CharField(max_length=20 , null=True, blank=True)
    group = models.CharField(max_length=20 , null=True, blank=True)
    student = models.ForeignKey(Student , related_name='curriculums' , on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation , related_name='curriculums' , on_delete=models.CASCADE)
    moyenne_rachat = models.FloatField(null=True, blank=True)
    moyenne_finale = models.FloatField(null=True, blank=True)
    moyenne_concours = models.FloatField(null=True, blank=True)
    moyenne_rattrapage = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20 , choices=Status.choices , null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['formation', 'rank']  
        verbose_name = 'Curriculum'
        verbose_name_plural = 'Curriculums'
        db_table = 'curriculum'
        unique_together = ['student', 'formation']  
        
    def __str__(self):
        return f'{self.student} - {self.formation} ({self.status})'  
