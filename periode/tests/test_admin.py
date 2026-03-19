from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from curriculum_module.models import Periode
from curriculum.models import Curriculum
from curriculum_module.admin import PeriodeAdmin


class PeriodeAdminTest(TestCase):
    """Tests for the Periode Admin interface."""

    def setUp(self):
        """Set up admin site, superuser, and test data."""
        self.site = AdminSite()
        self.admin = PeriodeAdmin(Periode, self.site)

        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
        )

        self.curriculum = Curriculum.objects.create(title='Curriculum Info')

        self.periode = Periode.objects.create(
            name='Semestre 1',
            curriculum=self.curriculum,
            credits=30,
            rank=1,
            moyenne=14.5,
        )

        self.client = Client()

    # ==================== ADMIN CONFIGURATION TESTS ====================

    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        expected = ['id', 'name', 'curriculum', 'credits', 'rank', 'moyenne', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected)

    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        expected = ['name', 'curriculum__student__first_name', 'curriculum__student__last_name']
        self.assertEqual(list(self.admin.search_fields), expected)

    def test_date_hierarchy(self):
        """Test that date_hierarchy is set to created_at."""
        self.assertEqual(self.admin.date_hierarchy, 'created_at')

    def test_readonly_fields(self):
        """Test that readonly_fields contains expected fields."""
        expected = ['id', 'curriculum', 'created_at']
        self.assertEqual(list(self.admin.readonly_fields), expected)

    # ==================== ADMIN ACCESS TESTS ====================

    def test_admin_login_required(self):
        """Test that admin requires authentication."""
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertEqual(response.status_code, 302)

    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertEqual(response.status_code, 200)

    def test_admin_changelist_displays_periodes(self):
        """Test that changelist displays periode data."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertContains(response, 'Semestre 1')
        self.assertContains(response, '30')
        self.assertContains(response, '1')

    def test_admin_add_page_accessible(self):
        """Test that add page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/add/')
        self.assertEqual(response.status_code, 200)

    def test_admin_change_page_accessible(self):
        """Test that change page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum_module/periode/{self.periode.id}/change/')
        self.assertEqual(response.status_code, 200)

    def test_admin_delete_page_accessible(self):
        """Test that delete page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum_module/periode/{self.periode.id}/delete/')
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN CRUD TESTS ====================

    def test_admin_create_periode(self):
        """Test creating a periode through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Semestre 2',
            'curriculum': self.curriculum.id,
            'credits': 25,
            'rank': 2,
            'moyenne': 13.0,
        }
        response = self.client.post('/admin/curriculum_module/periode/add/', data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Periode.objects.filter(name='Semestre 2').exists())

    def test_admin_create_without_optional_fields(self):
        """Test creating a periode without rank and moyenne through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Semestre Sans Options',
            'curriculum': self.curriculum.id,
            'credits': 20,
        }
        response = self.client.post('/admin/curriculum_module/periode/add/', data)
        self.assertEqual(response.status_code, 302)
        periode = Periode.objects.get(name='Semestre Sans Options')
        self.assertIsNone(periode.rank)
        self.assertIsNone(periode.moyenne)

    def test_admin_update_periode(self):
        """Test updating a periode through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Semestre 1 Updated',
            'curriculum': self.curriculum.id,
            'credits': 35,
            'rank': 1,
            'moyenne': 15.0,
        }
        response = self.client.post(
            f'/admin/curriculum_module/periode/{self.periode.id}/change/',
            data,
        )
        self.assertEqual(response.status_code, 302)
        self.periode.refresh_from_db()
        # name/credits should update; readonly fields won't change
        self.assertEqual(self.periode.credits, 35)

    def test_admin_delete_periode(self):
        """Test deleting a periode through admin."""
        self.client.login(username='admin', password='adminpass123')
        periode_id = self.periode.id
        response = self.client.post(
            f'/admin/curriculum_module/periode/{periode_id}/delete/',
            {'post': 'yes'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Periode.objects.filter(id=periode_id).exists())

    def test_admin_delete_periode_keeps_curriculum(self):
        """Test that deleting a periode does not delete the curriculum."""
        self.client.login(username='admin', password='adminpass123')
        curriculum_id = self.curriculum.id
        self.client.post(
            f'/admin/curriculum_module/periode/{self.periode.id}/delete/',
            {'post': 'yes'},
        )
        self.assertTrue(Curriculum.objects.filter(id=curriculum_id).exists())

    # ==================== ADMIN SEARCH TESTS ====================

    def test_admin_search_by_name(self):
        """Test searching periodes by name."""
        self.client.login(username='admin', password='adminpass123')
        Periode.objects.create(name='Autre Module', curriculum=self.curriculum, credits=10)
        response = self.client.get('/admin/curriculum_module/periode/?q=Semestre')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Semestre 1')
        self.assertNotContains(response, 'Autre Module')

    def test_admin_search_no_results(self):
        """Test search with no matching results."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/?q=Inexistant')
        self.assertEqual(response.status_code, 200)

    def test_admin_search_by_id(self):
        """Test searching by UUID."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum_module/periode/?q={self.periode.id}')
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN DISPLAY TESTS ====================

    def test_admin_displays_id(self):
        """Test that admin displays the periode ID."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertContains(response, str(self.periode.id))

    def test_admin_displays_name(self):
        """Test that admin displays the periode name."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertContains(response, self.periode.name)

    def test_admin_displays_credits(self):
        """Test that admin displays credits."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertContains(response, str(self.periode.credits))

    def test_admin_change_form_shows_readonly_fields(self):
        """Test that change form shows readonly fields."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum_module/periode/{self.periode.id}/change/')
        self.assertContains(response, str(self.periode.id))
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN READONLY FIELDS TESTS ====================

    def test_readonly_id_cannot_be_changed(self):
        """Test that ID cannot be changed via admin."""
        self.client.login(username='admin', password='adminpass123')
        import uuid
        new_id = uuid.uuid4()
        data = {
            'id': str(new_id),
            'name': 'Modified',
            'curriculum': self.curriculum.id,
            'credits': 30,
        }
        self.client.post(
            f'/admin/curriculum_module/periode/{self.periode.id}/change/',
            data,
        )
        self.periode.refresh_from_db()
        self.assertNotEqual(self.periode.id, new_id)

    def test_readonly_curriculum_cannot_be_changed_via_form(self):
        """Test that curriculum readonly field is not editable via form submission."""
        self.client.login(username='admin', password='adminpass123')
        curriculum2 = Curriculum.objects.create(title='New Curriculum')
        data = {
            'name': 'Modified',
            'curriculum': str(curriculum2.id),  # Attempt to change curriculum
            'credits': 30,
        }
        self.client.post(
            f'/admin/curriculum_module/periode/{self.periode.id}/change/',
            data,
        )
        self.periode.refresh_from_db()
        # Since curriculum is readonly, it should not have changed
        self.assertEqual(self.periode.curriculum, self.curriculum)

    # ==================== ADMIN VALIDATION TESTS ====================

    def test_admin_create_without_name_fails(self):
        """Test that creating without name shows error."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'curriculum': self.curriculum.id,
            'credits': 20,
        }
        response = self.client.post('/admin/curriculum_module/periode/add/', data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')

    def test_admin_create_without_credits_fails(self):
        """Test that creating without credits shows error."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Test Periode',
            'curriculum': self.curriculum.id,
        }
        response = self.client.post('/admin/curriculum_module/periode/add/', data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')

    # ==================== ADMIN PERMISSIONS TESTS ====================

    def test_non_superuser_cannot_access_admin(self):
        """Test that a regular user cannot access admin."""
        User.objects.create_user(username='regular', password='pass123')
        self.client.login(username='regular', password='pass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertIn(response.status_code, [302, 403])

    def test_staff_user_with_permissions_can_access(self):
        """Test that staff user with permissions can access admin."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        staff_user = User.objects.create_user(
            username='staff',
            password='staffpass123',
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Periode)
        permissions = Permission.objects.filter(content_type=content_type)
        staff_user.user_permissions.set(permissions)

        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN ORDERING TESTS ====================

    def test_admin_list_with_multiple_periodes(self):
        """Test admin list with multiple periodes."""
        self.client.login(username='admin', password='adminpass123')
        Periode.objects.create(name='Semestre 3', curriculum=self.curriculum, credits=20, rank=3)
        Periode.objects.create(name='Semestre 0', curriculum=self.curriculum, credits=10, rank=0)

        response = self.client.get('/admin/curriculum_module/periode/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Semestre 3')
        self.assertContains(response, 'Semestre 0')