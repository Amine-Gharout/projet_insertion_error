# module/tests/test_admin.py
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from module.models import Module
from module.admin import ModuleAdmin


class ModuleAdminTest(TestCase):
    """Tests for the Module Admin interface."""
    
    def setUp(self):
        """Set up admin site and test data."""
        self.site = AdminSite()
        self.admin = ModuleAdmin(Module, self.site)
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test module
        self.module = Module.objects.create(
            name='Algorithmique',
            code='ALGO101',
            description='Introduction aux algorithmes'
        )
        
        self.client = Client()
    
    # ==================== ADMIN CONFIGURATION TESTS ====================
    
    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        expected_fields = ['id', 'name', 'code', 'description', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        expected_fields = ['name', 'code', 'description']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        expected_fields = ['created_at']
        self.assertEqual(list(self.admin.list_filter), expected_fields)
    
    def test_ordering(self):
        """Test default ordering."""
        expected_ordering = ['name']
        self.assertEqual(list(self.admin.ordering), expected_ordering)
    
    def test_readonly_fields(self):
        """Test readonly fields."""
        expected_readonly = ['id', 'created_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)
    
    def test_date_hierarchy(self):
        """Test date hierarchy is set correctly."""
        self.assertEqual(self.admin.date_hierarchy, 'created_at')
    
    # ==================== ADMIN INTERFACE TESTS ====================
    
    def test_admin_login_required(self):
        """Test that admin interface requires authentication."""
        response = self.client.get('/admin/module/module/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/module/module/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_changelist_displays_modules(self):
        """Test that changelist displays modules."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/module/module/')
        
        self.assertContains(response, 'Algorithmique')
        self.assertContains(response, 'ALGO101')
    
    def test_admin_add_page_accessible(self):
        """Test that add module page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/module/module/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_change_page_accessible(self):
        """Test that change module page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/module/module/{self.module.id}/change/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_delete_page_accessible(self):
        """Test that delete module page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/module/module/{self.module.id}/delete/')
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN ACTIONS TESTS ====================
    
    def test_admin_create_module(self):
        """Test creating a module through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Base de données',
            'code': 'BDD201',
            'description': 'Gestion des bases de données'
        }
        response = self.client.post('/admin/module/module/add/', data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Module.objects.filter(code='BDD201').exists())
    
    def test_admin_update_module(self):
        """Test updating a module through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Algorithmique Avancée',
            'code': 'ALGO101',
            'description': 'Algorithmes avancés'
        }
        response = self.client.post(
            f'/admin/module/module/{self.module.id}/change/',
            data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        self.module.refresh_from_db()
        self.assertEqual(self.module.name, 'Algorithmique Avancée')
    
    def test_admin_delete_module(self):
        """Test deleting a module through admin."""
        self.client.login(username='admin', password='adminpass123')
        module_id = self.module.id
        
        response = self.client.post(
            f'/admin/module/module/{module_id}/delete/',
            {'post': 'yes'}
        )
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Module.objects.filter(id=module_id).exists())
    
    # ==================== ADMIN SEARCH TESTS ====================
    
    def test_admin_search_by_name(self):
        """Test searching modules by name in admin."""
        self.client.login(username='admin', password='adminpass123')
        Module.objects.create(name='Programmation', code='PROG001')
        
        response = self.client.get('/admin/module/module/?q=Algo')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algorithmique')
        self.assertNotContains(response, 'Programmation')
    
    def test_admin_search_by_code(self):
        """Test searching modules by code in admin."""
        self.client.login(username='admin', password='adminpass123')
        Module.objects.create(name='Programmation', code='PROG001')
        
        response = self.client.get('/admin/module/module/?q=PROG')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Programmation')
    
    def test_admin_search_by_description(self):
        """Test searching modules by description in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get('/admin/module/module/?q=algorithmes')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algorithmique')
    
    # ==================== ADMIN FILTER TESTS ====================
    
    def test_admin_filter_by_created_at(self):
        """Test filtering modules by created_at in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        # Get today's date for filtering
        from django.utils import timezone
        today = timezone.now().date()
        
        response = self.client.get(
            f'/admin/module/module/?created_at__day={today.day}'
            f'&created_at__month={today.month}'
            f'&created_at__year={today.year}'
        )
        
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN PERMISSIONS TESTS ====================
    
    def test_non_superuser_cannot_access_admin(self):
        """Test that regular user without permissions cannot access admin."""
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )
        self.client.login(username='regular', password='regularpass123')
        
        response = self.client.get('/admin/module/module/')
        
        # Should redirect to login or show forbidden
        self.assertIn(response.status_code, [302, 403])
    
    def test_staff_user_with_permissions_can_access(self):
        """Test that staff user with module permissions can access admin."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Add module permissions
        content_type = ContentType.objects.get_for_model(Module)
        permissions = Permission.objects.filter(content_type=content_type)
        staff_user.user_permissions.set(permissions)
        
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/module/module/')
        
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN VALIDATION TESTS ====================
    
    def test_admin_create_with_duplicate_code_fails(self):
        """Test that creating module with duplicate code fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Another Module',
            'code': 'ALGO101',  # Duplicate
            'description': 'Test'
        }
        response = self.client.post('/admin/module/module/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_admin_create_without_required_field_fails(self):
        """Test that creating module without required field fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Test Module',
            # Missing code field
            'description': 'Test'
        }
        response = self.client.post('/admin/module/module/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
