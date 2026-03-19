from django.contrib import admin
from .models import Grade

# Register your models here.
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin) :
    
    list_display = [
        'id' , 
        'period' ,
        'module' ,
        'note' ,
        'status' ,
        'source',
        'validated',
        'ects',
    ]
    
    search_fields = ['period__name' ]
    list_filter = ['status','source','validated']
    ordering = ['module'] 
    readonly_fields = ['id' , 'created_at', 'updated_at' , 'period', 'module'] #nzid period + module? or maybe we need to check them manually
    date_hierarchy = 'created_at'

