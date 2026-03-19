from django.contrib import admin
from .models import Program


# Register your models here.
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin) :
    
    list_display = [
        'id' , 
        'title' ,
        'code' ,
        'description' ,
        'cycle' ,
        'diploma' ,
        'speciality' ,
    ]
    
    search_fields = ['title' , 'code' , 'description' , 'cycle' , 'diploma', 'speciality']
    list_filter = ['cycle', 'diploma']
    ordering = ['title']
    date_hierarchy = 'created_at'
    readonly_fields = ['id' , 'created_at' ]
