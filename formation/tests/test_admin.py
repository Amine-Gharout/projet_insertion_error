# formation/tests/test_admin.py
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from formation.models import Formation
from program.models import Program
from formation.admin import FormationAdmin


class FormationAdminTest(TestCase):
    """Tests for the Formation Admin interface."""
    
    def setUp(self):
        """Set up admin site and test data."""
        self.site = AdminSite()
        self.admin = FormationAdmin(Formation, self.site)
        
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
        
        self.client = Client()
    
    # ==================== ADMIN CONFIGURATION TESTS ====================
    
    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        expected_fields = ['id', 'name', 'year', 'program', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        expected_fields = ['id', 'name', 'year', 'program']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        expected_fields = ['name', 'year', 'program']
        self.assertEqual(list(self.admin.list_filter), expected_fields)
    
    def test_ordering(self):
        """Test default ordering."""
        expected_ordering = ['year']
        self.assertEqual(list(self.admin.ordering), expected_ordering)
    
    def test_readonly_fields(self):
        """Test readonly fields."""
        expected_readonly = ['id', 'program', 'name', 'year']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)
    
    def test_date_hierarchy(self):
        """Test date hierarchy is set correctly."""
        self.assertEqual(self.admin.date_hierarchy, 'created_at')
    
    # ==================== ADMIN INTERFACE TESTS ====================
    
    def test_admin_login_required(self):
        """Test that admin interface requires authentication."""
        response = self.client.get('/admin/formation/formation/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/formation/formation/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_changelist_displays_formations(self):
        """Test that changelist displays formations."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/formation/formation/')
        
        self.assertContains(response, 'Promotion 2024')
        self.assertContains(response, '2024')
        self.assertContains(response, 'Informatique')
    
    def test_admin_add_page_accessible(self):
        """Test that add formation page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/formation/formation/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_change_page_accessible(self):
        """Test that change formation page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/formation/formation/{self.formation.id}/change/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_delete_page_accessible(self):
        """Test that delete formation page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/formation/formation/{self.formation.id}/delete/')
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN ACTIONS TESTS ====================
    
    def test_admin_create_formation(self):
        """Test creating a formation through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Promotion 2025',
            'year': 2025,
            'program': self.program.id
        }
        response = self.client.post('/admin/formation/formation/add/', data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Formation.objects.filter(name='Promotion 2025').exists())
    
    def test_admin_update_formation(self):
        """Test updating a formation through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Promotion 2024 - Updated',
            'year': 2024,
            'program': self.program.id
        }
        response = self.client.post(
            f'/admin/formation/formation/{self.formation.id}/change/',
            data
        )
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        self.formation.refresh_from_db()
        self.assertEqual(self.formation.name, 'Promotion 2024 - Updated')
    
    def test_admin_delete_formation(self):
        """Test deleting a formation through admin."""
        self.client.login(username='admin', password='adminpass123')
        formation_id = self.formation.id
        
        response = self.client.post(
            f'/admin/formation/formation/{formation_id}/delete/',
            {'post': 'yes'}
        )
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Formation.objects.filter(id=formation_id).exists())
    
    def test_admin_delete_formation_keeps_program(self):
        """Test that deleting formation doesn't delete the program."""
        self.client.login(username='admin', password='adminpass123')
        program_id = self.program.id
        
        self.client.post(
            f'/admin/formation/formation/{self.formation.id}/delete/',
            {'post': 'yes'}
        )
        
        # Program should still exist
        self.assertTrue(Program.objects.filter(id=program_id).exists())
    
    # ==================== ADMIN SEARCH TESTS ====================
    
    def test_admin_search_by_name(self):
        """Test searching formations by name in admin."""
        self.client.login(username='admin', password='adminpass123')
        Formation.objects.create(
            name='Autre Formation',
            year=2025,
            program=self.program
        )
        
        response = self.client.get('/admin/formation/formation/?q=Promotion')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promotion 2024')
        self.assertNotContains(response, 'Autre Formation')
    
    def test_admin_search_by_year(self):
        """Test searching formations by year in admin."""
        self.client.login(username='admin', password='adminpass123')
        Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        response = self.client.get('/admin/formation/formation/?q=2025')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2025')
    
    def test_admin_search_by_id(self):
        """Test searching formations by ID in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(f'/admin/formation/formation/?q={self.formation.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promotion 2024')
    
    # ==================== ADMIN FILTER TESTS ====================
    
    def test_admin_filter_by_year(self):
        """Test filtering formations by year in admin."""
        self.client.login(username='admin', password='adminpass123')
        Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        response = self.client.get('/admin/formation/formation/?year=2024')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promotion 2024')
    
    def test_admin_filter_by_program(self):
        """Test filtering formations by program in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        Formation.objects.create(
            name='Math Promo',
            year=2024,
            program=program2
        )
        
        response = self.client.get(f'/admin/formation/formation/?program__id__exact={self.program.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promotion 2024')
    
    def test_admin_filter_by_created_at(self):
        """Test filtering formations by created_at in admin."""
        self.client.login(username='admin', password='adminpass123')
        
        # Get today's date for filtering
        from django.utils import timezone
        today = timezone.now().date()
        
        response = self.client.get(
            f'/admin/formation/formation/?created_at__day={today.day}'
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
        
        response = self.client.get('/admin/formation/formation/')
        
        # Should redirect to login or show forbidden
        self.assertIn(response.status_code, [302, 403])
    
    def test_staff_user_with_permissions_can_access(self):
        """Test that staff user with formation permissions can access admin."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Add formation permissions
        content_type = ContentType.objects.get_for_model(Formation)
        permissions = Permission.objects.filter(content_type=content_type)
        staff_user.user_permissions.set(permissions)
        
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/formation/formation/')
        
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN VALIDATION TESTS ====================
    
    def test_admin_create_without_required_field_name_fails(self):
        """Test that creating formation without name fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            # Missing name field
            'year': 2024,
            'program': self.program.id
        }
        response = self.client.post('/admin/formation/formation/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_required_field_year_fails(self):
        """Test that creating formation without year fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Test Formation',
            # Missing year field
            'program': self.program.id
        }
        response = self.client.post('/admin/formation/formation/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_without_required_field_program_fails(self):
        """Test that creating formation without program fails in admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Test Formation',
            'year': 2024,
            # Missing program field
        }
        response = self.client.post('/admin/formation/formation/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
    
    def test_admin_create_with_nonexistent_program_fails(self):
        """Test that creating formation with nonexistent program fails."""
        self.client.login(username='admin', password='adminpass123')
        import uuid
        data = {
            'name': 'Test Formation',
            'year': 2024,
            'program': uuid.uuid4()  # Non-existent
        }
        response = self.client.post('/admin/formation/formation/add/', data)
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN DISPLAY TESTS ====================
    
    def test_admin_displays_all_list_fields(self):
        """Test that admin changelist displays all list_display fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/formation/formation/')
        
        # Check all list_display fields are visible
        self.assertContains(response, str(self.formation.id))
        self.assertContains(response, self.formation.name)
        self.assertContains(response, str(self.formation.year))
        self.assertContains(response, self.program.title)
    
    def test_admin_change_form_shows_readonly_fields(self):
        """Test that change form shows readonly fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/formation/formation/{self.formation.id}/change/')
        
        # ID, program, name, year should be visible but readonly
        self.assertContains(response, str(self.formation.id))
        self.assertContains(response, self.formation.name)
        self.assertEqual(response.status_code, 200)
    
    # ==================== ADMIN READONLY FIELDS TESTS ====================
    
    def test_admin_readonly_prevents_editing_id(self):
        """Test that ID field is readonly and cannot be changed."""
        self.client.login(username='admin', password='adminpass123')
        import uuid
        new_id = uuid.uuid4()
        data = {
            'id': new_id,
            'name': 'Updated',
            'year': 2025,
            'program': self.program.id
        }
        response = self.client.post(
            f'/admin/formation/formation/{self.formation.id}/change/',
            data
        )
        
        self.formation.refresh_from_db()
        # ID should not have changed
        self.assertNotEqual(self.formation.id, new_id)
    
    # ==================== ADMIN ORDERING TESTS ====================
    
    def test_admin_respects_default_ordering(self):
        """Test that admin list respects default ordering by year."""
        self.client.login(username='admin', password='adminpass123')
        
        # Create formations in non-chronological order
        Formation.objects.create(name='Promo 2026', year=2026, program=self.program)
        Formation.objects.create(name='Promo 2023', year=2023, program=self.program)
        
        response = self.client.get('/admin/formation/formation/')
        
        self.assertEqual(response.status_code, 200)
        # Formations should appear in year order
        content = response.content.decode()
        pos_2023 = content.find('2023')
        pos_2024 = content.find('2024')
        pos_2026 = content.find('2026')
        
        self.assertLess(pos_2023, pos_2024)
        self.assertLess(pos_2024, pos_2026)
    
    # ==================== ADMIN FOREIGN KEY TESTS ====================
    
    def test_admin_displays_program_in_dropdown(self):
        """Test that program appears in dropdown on add/change forms."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/formation/formation/add/')
        
        # Program should be in dropdown
        self.assertContains(response, self.program.title)
        self.assertEqual(response.status_code, 200)
    
    def test_admin_multiple_programs_in_dropdown(self):
        """Test that multiple programs appear in dropdown."""
        self.client.login(username='admin', password='adminpass123')
        
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        response = self.client.get('/admin/formation/formation/add/')
        
        # Both programs should be in dropdown
        self.assertContains(response, self.program.title)
        self.assertContains(response, program2.title)
