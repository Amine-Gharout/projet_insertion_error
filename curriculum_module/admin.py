from django.contrib import admin
from .models import Curriculum_module

# Register your models here.
@admin.register(Curriculum_module)
class Curriculum_module_Admin(admin.ModelAdmin) :
    list_display = ['id' , 'formation' , 'module' , 'coefficient' , 'created_at'] 
    search_fields = ['formation__name' , 'module__name' , 'semester' , 'year']
    ordering = ['created_at' , 'formation__name' , 'module__name' , 'coefficient' , 'NE' , 'semester' , 'year']
    date_hierarchy = 'created_at'
    readonly_fields = ['id' , 'formation' , 'module'  , 'created_at']
