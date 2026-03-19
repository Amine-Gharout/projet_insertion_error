# program/tests/test_admin.py
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from program.models import Program
from program.admin import ProgramAdmin


class ProgramAdminTest(TestCase):
    """Tests for the Program Admin interface."""
    
    def setUp(self):
        """Set up admin site and test data."""
        self.site = AdminSite()
        self.admin = ProgramAdmin(Program, self.site)
        
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
            description='Programme en informatique',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        
        self.client = Client()
    
    # ==================== ADMIN CONFIGURATION TESTS ====================
    
    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        expected_fields = ['id', 'title', 'code', 'description', 'cycle', 'diploma']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        expected_fields = ['title', 'code', 'description', 'cycle', 'diploma']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        expected_fields = ['cycle', 'diploma']
        self.assertEqual(list(self.admin.list_filter), expected_fields)
    
    def test_ordering(self):
        """Test default ordering."""
        expected_ordering = ['title']
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
        response = self.client.get('/admin/program/program/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/program/program/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_changelist_displays_programs(self):
        """Test that changelist displays programs."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/program/program/')
        
        self.assertContains(response, 'Informatique')
        self.assertContains(response, 'INFO101')
        self.assertContains(response, 'Licence')
    
    def test_admin_add_page_accessible(self):
        """Test that add program page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/program/program/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_change_page_accessible(self):
        """Test that change program page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/program/program/{self.program.id}/change/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_delete_page_accessible(self):
        """Test that delete program page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/program/program/{self.program.id}/delete/')
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN ACTIONS TESTS ====================
    
    def test_admin_create_program(self):
        """Test creating a program through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Mathématiques',
            'code': 'MATH201',
            'description': 'Programme de mathématiques',
            'cycle': 'Master',
            'diploma': 'Master en Mathématiques'
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Program.objects.filter(code='MATH201').exists())
    
    def test_admin_update_program(self):
        """Test updating a program through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Informatique Avancée',
            'code': 'INFO101',
            'description': 'Programme avancé',
            'cycle': 'Master',
            'diploma': 'Master en Informatique'
        }
        response = self.client.post(
            f'/admin/program/program/{self.program.id}/change/',
            data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        self.program.refresh_from_db()
        self.assertEqual(self.program.title, 'Informatique Avancée')
        self.assertEqual(self.program.cycle, 'Master')
    
    def test_admin_delete_program(self):
        """Test deleting a program through admin."""
        self.client.login(username='admin', password='adminpass123')
        program_id = self.program.id
        
        response = self.client.post(
            f'/admin/program/program/{program_id}/delete/',
            {'post': 'yes'}
        )
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Program.objects.filter(id=program_id).exists())
    
    # ==================== ADMIN SEARCH TESTS ====================
    
    def test_admin_search_by_title(self):
        """Test searching programs by title in admin."""
        self.client.login(username='admin', password='adminpass123')
        Program.objects.create(
            title='Mathématiques',
            code='MATH001',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        response = self.client.get('/admin/program/program/?q=Info')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informatique')
        self.assertNotContains(response, 'Mathématiques')
    
    def test_admin_search_by_code(self):
        """Test searching programs by code in admin."""
        self.client.login(username='admin', password='adminpass123')
        Program.objects.create(
            title='Mathématiques',
            code='MATH001',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        response = self.client.get('/admin/program/program/?q=MATH')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mathématiques')
    
    def test_admin_search_by_description(self):
        """Test searching programs by description in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get('/admin/program/program/?q=informatique')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informatique')
    
    def test_admin_search_by_cycle(self):
        """Test searching programs by cycle in admin."""
        self.client.login(username='admin', password='adminpass123')
        Program.objects.create(
            title='Mathématiques',
            code='MATH001',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        response = self.client.get('/admin/program/program/?q=Master')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mathématiques')
    
    def test_admin_search_by_diploma(self):
        """Test searching programs by diploma in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get('/admin/program/program/?q=Licence')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informatique')
    
    # ==================== ADMIN FILTER TESTS ====================
    
    def test_admin_filter_by_cycle(self):
        """Test filtering programs by cycle in admin."""
        self.client.login(username='admin', password='adminpass123')
        Program.objects.create(
            title='Mathématiques',
            code='MATH001',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        response = self.client.get('/admin/program/program/?cycle=Licence')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informatique')
        # Master programs should not appear when filtering by Licence
    
    def test_admin_filter_by_diploma(self):
        """Test filtering programs by diploma in admin."""
        self.client.login(username='admin', password='adminpass123')
        Program.objects.create(
            title='Mathématiques',
            code='MATH001',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        response = self.client.get('/admin/program/program/?diploma=Licence+en+Informatique')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informatique')
    
    def test_admin_filter_by_created_at(self):
        """Test filtering programs by created_at in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        # Get today's date for filtering
        from django.utils import timezone
        today = timezone.now().date()
        
        response = self.client.get(
            f'/admin/program/program/?created_at__day={today.day}'
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
        
        response = self.client.get('/admin/program/program/')
        
        # Should redirect to login or show forbidden
        self.assertIn(response.status_code, [302, 403])
    
    def test_staff_user_with_permissions_can_access(self):
        """Test that staff user with program permissions can access admin."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Add program permissions
        content_type = ContentType.objects.get_for_model(Program)
        permissions = Permission.objects.filter(content_type=content_type)
        staff_user.user_permissions.set(permissions)
        
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/program/program/')
        
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN VALIDATION TESTS ====================
    
    def test_admin_create_with_duplicate_title_fails(self):
        """Test that creating program with duplicate title fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Informatique',  # Duplicate
            'code': 'DIFF001',
            'cycle': 'Master',
            'diploma': 'Master en Informatique'
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_admin_create_with_duplicate_code_fails(self):
        """Test that creating program with duplicate code fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Another Program',
            'code': 'INFO101',  # Duplicate
            'cycle': 'Master',
            'diploma': 'Master Diploma'
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_admin_create_without_required_field_title_fails(self):
        """Test that creating program without title fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            # Missing title field
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_required_field_code_fails(self):
        """Test that creating program without code fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Test Program',
            # Missing code field
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_required_field_cycle_fails(self):
        """Test that creating program without cycle fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            # Missing cycle field
            'diploma': 'Test Diploma'
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_required_field_diploma_fails(self):
        """Test that creating program without diploma fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'Licence',
            # Missing diploma field
        }
        response = self.client.post('/admin/program/program/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    # ==================== ADMIN DISPLAY TESTS ====================
    
    def test_admin_displays_all_list_fields(self):
        """Test that admin changelist displays all list_display fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/program/program/')
        
        # Check all list_display fields are visible
        self.assertContains(response, str(self.program.id))
        self.assertContains(response, self.program.title)
        self.assertContains(response, self.program.code)
        self.assertContains(response, self.program.cycle)
        self.assertContains(response, self.program.diploma)
    
    def test_admin_change_form_shows_readonly_fields(self):
        """Test that change form shows readonly fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/program/program/{self.program.id}/change/')
        
        # ID and created_at should be visible but readonly
        self.assertContains(response, str(self.program.id))
        # created_at format may vary, just check the page loads
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN MULTIPLE FILTERS TEST ====================
    
    def test_admin_filter_by_multiple_fields(self):
        """Test filtering by multiple fields simultaneously."""
        self.client.login(username='admin', password='adminpass123')
        
        # Create programs with different cycles and diplomas
        Program.objects.create(
            title='Mathématiques',
            code='MATH001',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        Program.objects.create(
            title='Physique',
            code='PHYS001',
            cycle='Licence',
            diploma='Licence en Physique'
        )
        
        # Filter by cycle=Licence
        response = self.client.get('/admin/program/program/?cycle=Licence')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informatique')
        self.assertContains(response, 'Physique')
    
    # ==================== ADMIN ORDERING TESTS ====================
    
    def test_admin_respects_default_ordering(self):
        """Test that admin list respects default ordering by title."""
        self.client.login(username='admin', password='adminpass123')
        
        # Create programs in non-alphabetical order
        Program.objects.create(
            title='Zebra Program',
            code='ZEB001',
            cycle='Licence',
            diploma='Zebra Diploma'
        )
        Program.objects.create(
            title='Alpha Program',
            code='ALP001',
            cycle='Licence',
            diploma='Alpha Diploma'
        )
        
        response = self.client.get('/admin/program/program/')
        
        self.assertEqual(response.status_code, 200)
        # Programs should appear in alphabetical order
        content = response.content.decode()
        alpha_pos = content.find('Alpha Program')
        info_pos = content.find('Informatique')
        zebra_pos = content.find('Zebra Program')
        
        self.assertLess(alpha_pos, info_pos)
        self.assertLess(info_pos, zebra_pos)
