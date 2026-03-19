from django.contrib import admin
from .models import Curriculum

# Register your models here.
@admin.register(Curriculum)
class Curriculum_Admin(admin.ModelAdmin) :
    list_display = ['id', 'student', 'formation', 'section', 'group', 'status','rank','moyenne_finale' ,'created_at', 'updated_at']
    search_fields = ['student__first_name', 'student__last_name', 'formation__name', 'section', 'group', 'status']
    ordering = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'student', 'formation', 'created_at', 'updated_at']
    list_filter = ['status', 'formation__name', 'section', 'group']
    
