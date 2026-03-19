from django.contrib import admin
from .models import Periode

# Register your models here.
@admin.register(Periode)
class PeriodeAdmin(admin.ModelAdmin) :
    list_display = ['id', 'name', 'curriculum', 'credits', 'rank', 'moyenne', 'created_at']
    search_fields = ['name', 'curriculum__student__first_name', 'curriculum__student__last_name']
    list_filter = ['curriculum__formation', 'credits', 'rank', 'moyenne']
    ordering = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'curriculum', 'created_at']
    
