from django.db import models
import uuid

class Student(models.Model) :
    
    class Sexe(models.TextChoices) :
        MALE = 'Male' 
        FEMALE = 'Female'
        NULL = 'Null'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(max_length=20 , null=True , blank=True) 
    first_name = models.CharField(max_length=60) 
    last_name = models.CharField(max_length=60)
    birth_date = models.DateField(null=True , blank=True)
    birth_place = models.CharField(max_length=100, null=True, blank=True)
    sexe = models.CharField(max_length=10, null=True, blank=True , choices=Sexe.choices)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  
    
    class Meta :
        unique_together = ('first_name', 'last_name')
        ordering = ['first_name', 'last_name', 'matricule']
        verbose_name = 'Etudiant'
        verbose_name_plural = 'Etudiants'
        db_table = 'student'
        
    def __str__(self) -> str:
        return f"{self.matricule} - {self.first_name} {self.last_name}"
    
    
    
     
    