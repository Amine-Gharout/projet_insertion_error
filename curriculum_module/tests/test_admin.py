# curriculum_module/tests/test_admin.py
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from curriculum_module.models import CurriculumModule
from formation.models import Formation
from program.models import Program
from module.models import Module
from curriculum_module.admin import CurriculumModuleAdmin


class CurriculumModuleAdminTest(TestCase):
    """Tests for the CurriculumModule Admin interface."""
    
    def setUp(self):
        """Set up admin site and test data."""
        self.site = AdminSite()
        self.admin = CurriculumModuleAdmin(CurriculumModule, self.site)
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test program
        self.program = Program.objects.create(
            title='Informatique',
            code='INFO101',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        
        # Create test formation
        self.formation = Formation.objects.create(
            name='Promotion 2024',
            year=2024,
            program=self.program
        )
        
        # Create test modules
        self.module1 = Module.objects.create(
            name='Algorithmique',
            code='ALGO101'
        )
        self.module2 = Module.objects.create(
            name='Base de données',
            code='BDD201'
        )
        
        # Create test curriculum module
        self.curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module1,
            coefficient=3
        )
        
        self.client = Client()
    
    # ==================== ADMIN CONFIGURATION TESTS ====================
    
    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        expected_fields = ['id', 'formation', 'module', 'coefficient', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        expected_fields = ['formation__name', 'module__name', 'module__code']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        expected_fields = ['formation', 'module', 'coefficient']
        self.assertEqual(list(self.admin.list_filter), expected_fields)
    
    def test_ordering(self):
        """Test default ordering."""
        expected_ordering = ['formation', 'module']
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
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_changelist_displays_curriculum_modules(self):
        """Test that changelist displays curriculum modules."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        
        self.assertContains(response, 'Promotion 2024')
        self.assertContains(response, 'Algorithmique')
        self.assertContains(response, '3')
    
    def test_admin_add_page_accessible(self):
        """Test that add curriculum module page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_change_page_accessible(self):
        """Test that change curriculum module page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            f'/admin/curriculum_module/curriculummodule/{self.curriculum_module.id}/change/'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_admin_delete_page_accessible(self):
        """Test that delete curriculum module page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            f'/admin/curriculum_module/curriculummodule/{self.curriculum_module.id}/delete/'
        )
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN ACTIONS TESTS ====================
    
    def test_admin_create_curriculum_module(self):
        """Test creating a curriculum module through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'formation': self.formation.id,
            'module': self.module2.id,
            'coefficient': 2
        }
        response = self.client.post(
            '/admin/curriculum_module/curriculummodule/add/',
            data
        )
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CurriculumModule.objects.filter(
                formation=self.formation,
                module=self.module2
            ).exists()
        )
    
    def test_admin_update_curriculum_module(self):
        """Test updating a curriculum module through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'formation': self.formation.id,
            'module': self.module1.id,
            'coefficient': 5
        }
        response = self.client.post(
            f'/admin/curriculum_module/curriculummodule/{self.curriculum_module.id}/change/',
            data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        self.curriculum_module.refresh_from_db()
        self.assertEqual(self.curriculum_module.coefficient, 5)
    
    def test_admin_delete_curriculum_module(self):
        """Test deleting a curriculum module through admin."""
        self.client.login(username='admin', password='adminpass123')
        cm_id = self.curriculum_module.id
        
        response = self.client.post(
            f'/admin/curriculum_module/curriculummodule/{cm_id}/delete/',
            {'post': 'yes'}
        )
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CurriculumModule.objects.filter(id=cm_id).exists())
    
    def test_admin_delete_keeps_formation_and_module(self):
        """Test that deleting curriculum module doesn't delete formation or module."""
        self.client.login(username='admin', password='adminpass123')
        formation_id = self.formation.id
        module_id = self.module1.id
        
        self.client.post(
            f'/admin/curriculum_module/curriculummodule/{self.curriculum_module.id}/delete/',
            {'post': 'yes'}
        )
        
        # Both should still exist
        self.assertTrue(Formation.objects.filter(id=formation_id).exists())
        self.assertTrue(Module.objects.filter(id=module_id).exists())
    
    # ==================== ADMIN SEARCH TESTS ====================
    
    def test_admin_search_by_formation_name(self):
        """Test searching by formation name in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        formation2 = Formation.objects.create(
            name='Other Formation',
            year=2025,
            program=self.program
        )
        CurriculumModule.objects.create(
            formation=formation2,
            module=self.module2,
            coefficient=2
        )
        
        response = self.client.get(
            '/admin/curriculum_module/curriculummodule/?q=Promotion'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promotion 2024')
        self.assertNotContains(response, 'Other Formation')
    
    def test_admin_search_by_module_name(self):
        """Test searching by module name in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(
            '/admin/curriculum_module/curriculummodule/?q=Algorithmique'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algorithmique')
    
    def test_admin_search_by_module_code(self):
        """Test searching by module code in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(
            '/admin/curriculum_module/curriculummodule/?q=ALGO101'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ALGO101')
    
    # ==================== ADMIN FILTER TESTS ====================
    
    def test_admin_filter_by_formation(self):
        """Test filtering by formation in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        formation2 = Formation.objects.create(
            name='Formation 2',
            year=2025,
            program=self.program
        )
        CurriculumModule.objects.create(
            formation=formation2,
            module=self.module2,
            coefficient=2
        )
        
        response = self.client.get(
            f'/admin/curriculum_module/curriculummodule/?formation__id__exact={self.formation.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promotion 2024')
    
    def test_admin_filter_by_module(self):
        """Test filtering by module in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        response = self.client.get(
            f'/admin/curriculum_module/curriculummodule/?module__id__exact={self.module1.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algorithmique')
    
    def test_admin_filter_by_coefficient(self):
        """Test filtering by coefficient in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=3
        )
        
        response = self.client.get(
            '/admin/curriculum_module/curriculummodule/?coefficient=3'
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_admin_filter_by_created_at(self):
        """Test filtering by created_at in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        from django.utils import timezone
        today = timezone.now().date()
        
        response = self.client.get(
            f'/admin/curriculum_module/curriculummodule/?created_at__day={today.day}'
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
        
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        
        # Should redirect to login or show forbidden
        self.assertIn(response.status_code, [302, 403])
    
    def test_staff_user_with_permissions_can_access(self):
        """Test that staff user with permissions can access admin."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Add curriculum module permissions
        content_type = ContentType.objects.get_for_model(CurriculumModule)
        permissions = Permission.objects.filter(content_type=content_type)
        staff_user.user_permissions.set(permissions)
        
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN VALIDATION TESTS ====================
    
    def test_admin_create_without_formation_fails(self):
        """Test that creating without formation fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'module': self.module1.id,
            'coefficient': 3
        }
        response = self.client.post(
            '/admin/curriculum_module/curriculummodule/add/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_module_fails(self):
        """Test that creating without module fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'formation': self.formation.id,
            'coefficient': 3
        }
        response = self.client.post(
            '/admin/curriculum_module/curriculummodule/add/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_coefficient_fails(self):
        """Test that creating without coefficient fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'formation': self.formation.id,
            'module': self.module1.id
        }
        response = self.client.post(
            '/admin/curriculum_module/curriculummodule/add/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_duplicate_fails(self):
        """Test that creating duplicate formation-module fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'formation': self.formation.id,
            'module': self.module1.id,  # Already exists
            'coefficient': 5
        }
        response = self.client.post(
            '/admin/curriculum_module/curriculummodule/add/',
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    # ==================== ADMIN DISPLAY TESTS ====================
    
    def test_admin_displays_all_list_fields(self):
        """Test that admin changelist displays all list_display fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        
        # Check all list_display fields are visible
        self.assertContains(response, str(self.curriculum_module.id))
        self.assertContains(response, str(self.formation))
        self.assertContains(response, str(self.module1))
        self.assertContains(response, '3')
    
    def test_admin_change_form_shows_readonly_fields(self):
        """Test that change form shows readonly fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            f'/admin/curriculum_module/curriculummodule/{self.curriculum_module.id}/change/'
        )
        
        # ID and created_at should be visible but readonly
        self.assertContains(response, str(self.curriculum_module.id))
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN FOREIGN KEY TESTS ====================
    
    def test_admin_displays_formation_dropdown(self):
        """Test that formation appears in dropdown on add/change forms."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/add/')
        
        # Formation should be in dropdown
        self.assertContains(response, self.formation.name)
        self.assertEqual(response.status_code, 200)
    
    def test_admin_displays_module_dropdown(self):
        """Test that module appears in dropdown on add/change forms."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/curriculummodule/add/')
        
        # Module should be in dropdown
        self.assertContains(response, self.module1.name)
        self.assertEqual(response.status_code, 200)
    
    def test_admin_multiple_formations_in_dropdown(self):
        """Test that multiple formations appear in dropdown."""
        self.client.login(username='admin', password='adminpass123')
        
        formation2 = Formation.objects.create(
            name='Formation 2',
            year=2025,
            program=self.program
        )
        
        response = self.client.get('/admin/curriculum_module/curriculummodule/add/')
        
        # Both formations should be in dropdown
        self.assertContains(response, self.formation.name)
        self.assertContains(response, formation2.name)
    
    def test_admin_multiple_modules_in_dropdown(self):
        """Test that multiple modules appear in dropdown."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get('/admin/curriculum_module/curriculummodule/add/')
        
        # Both modules should be in dropdown
        self.assertContains(response, self.module1.name)
        self.assertContains(response, self.module2.name)
    
    # ==================== ADMIN ORDERING TESTS ====================
    
    def test_admin_respects_default_ordering(self):
        """Test that admin list respects default ordering."""
        self.client.login(username='admin', password='adminpass123')
        
        formation2 = Formation.objects.create(
            name='Alpha Formation',
            year=2023,
            program=self.program
        )
        CurriculumModule.objects.create(
            formation=formation2,
            module=self.module2,
            coefficient=2
        )
        
        response = self.client.get('/admin/curriculum_module/curriculummodule/')
        
        self.assertEqual(response.status_code, 200)
        # Should be ordered by formation, then module
    
    # ==================== ADMIN SELECT_RELATED OPTIMIZATION ====================
    
    def test_admin_queryset_uses_select_related(self):
        """Test that admin queryset uses select_related for performance."""
        # This test verifies the get_queryset optimization
        queryset = self.admin.get_queryset(None)
        
        # Check that the queryset has select_related
        self.assertIn('formation', queryset.query.select_related)
        self.assertIn('module', queryset.query.select_related)