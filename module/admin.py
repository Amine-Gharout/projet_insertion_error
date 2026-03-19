from django.contrib import admin
from .models import Module

# Register your models here.
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin) :
    
    list_display = [
        'id' , 
        'name' ,
        'code' ,
        'description' ,
        'created_at' ,
    ]
    
    search_fields = ['name' , 'code' , 'description']
    list_filter = ['created_at']
    ordering = ['name']
    date_hierarchy = 'created_at'
    readonly_fields = ['id' , 'created_at' ]

