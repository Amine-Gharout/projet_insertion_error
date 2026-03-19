from django.contrib import admin
from .models import Formation

# Register your models here.
@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin) :
    list_display = [
        'id' , 
        'name' , 
        'program' , 
        'created_at' 
     ] 
    
    search_fields = [ 'name' , 'program__name']
    
    list_filter = [ 'created_at' , 'program']
    
    ordering= ['created_at'] 
    
    date_hierarchy = 'created_at'
    
    readonly_fields = ['id' , 'program' , 'name' , 'created_at']
    
