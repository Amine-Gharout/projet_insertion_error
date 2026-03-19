# student/admin.py
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Configuration de l'interface admin pour Student."""
    
    # Columns to display in the list view
    list_display = [
        'matricule',
        'full_name',           # Custom method (see below)
        'birth_date',       # Use your actual field name
        'created_at'
    ]
    
    # Fields that can be searched
    search_fields = ['matricule', 'first_name', 'last_name']
    
    # Sidebar filters
    list_filter = ['created_at', 'birth_date']
    
    # Default sorting
    ordering = ['-matricule']
    
    # Add date hierarchy navigation
    date_hierarchy = 'created_at'
    
    # Read-only fields
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    # Custom method to display full name
    @admin.display(description='Nom complet')
    def full_name(self, obj):
        """Display student's full name."""
        return f"{obj.first_name} {obj.last_name}"