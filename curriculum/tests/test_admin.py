from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from curriculum.models import Curriculum
from student.models import Student
from formation.models import Formation
from curriculum.admin import Curriculum_Admin


class CurriculumAdminTest(TestCase):
    """Tests for the Curriculum Admin interface."""

    def setUp(self):
        """Set up admin site, superuser, and test data."""
        self.site = AdminSite()
        self.admin = Curriculum_Admin(Curriculum, self.site)

        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
        )

        self.student = Student.objects.create(
            first_name='Mohammed',
            last_name='Merzougui',
            matricule='E074001',
        )
        self.student2 = Student.objects.create(
            first_name='Karim',
            last_name='Merzouk',
            matricule='E074002',
        )
        self.formation = Formation.objects.create(name='Promotion 2024', year=2024)
        self.formation2 = Formation.objects.create(name='Promotion 2025', year=2025)

        self.curriculum = Curriculum.objects.create(
            student=self.student,
            formation=self.formation,
            section='A',
            group='G1',
            status='active',
            rank=1,
            moyenne_finale=14.5,
        )

        self.client = Client()

    # ==================== ADMIN CONFIGURATION TESTS ====================

    def test_list_display_fields(self):
        """Test list_display contains expected fields."""
        expected = ['id', 'student', 'formation', 'section', 'group', 'status', 'created_at', 'updated_at']
        self.assertEqual(list(self.admin.list_display), expected)

    def test_search_fields(self):
        """Test search_fields contains expected fields."""
        expected = [
            'student__first_name', 'student__last_name',
            'formation__name', 'section', 'group', 'status'
        ]
        self.assertEqual(list(self.admin.search_fields), expected)

    def test_date_hierarchy(self):
        """Test date_hierarchy is set to created_at."""
        self.assertEqual(self.admin.date_hierarchy, 'created_at')

    def test_readonly_fields(self):
        """Test readonly_fields contains expected fields."""
        expected = ['id', 'student', 'formation', 'section', 'group', 'status', 'created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected)

    # ==================== ADMIN ACCESS TESTS ====================

    def test_admin_login_required(self):
        """Test that admin requires authentication."""
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertEqual(response.status_code, 302)

    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertEqual(response.status_code, 200)

    def test_admin_changelist_displays_data(self):
        """Test that changelist displays curriculum data."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertContains(response, 'active')
        self.assertContains(response, 'A')

    def test_admin_add_page_accessible(self):
        """Test that add page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/add/')
        self.assertEqual(response.status_code, 200)

    def test_admin_change_page_accessible(self):
        """Test that change page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum/curriculum/{self.curriculum.id}/change/')
        self.assertEqual(response.status_code, 200)

    def test_admin_delete_page_accessible(self):
        """Test that delete page is accessible."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum/curriculum/{self.curriculum.id}/delete/')
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN CRUD TESTS ====================

    def test_admin_create_curriculum(self):
        """Test creating a curriculum through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'student': self.student2.id,
            'formation': self.formation.id,
            'section': 'B',
            'group': 'G2',
            'status': 'active',
            'rank': 2,
        }
        response = self.client.post('/admin/curriculum/curriculum/add/', data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Curriculum.objects.filter(student=self.student2, formation=self.formation).exists())

    def test_admin_create_without_optional_fields(self):
        """Test creating curriculum without optional fields."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'student': self.student2.id,
            'formation': self.formation.id,
            'status': 'active',
        }
        response = self.client.post('/admin/curriculum/curriculum/add/', data)
        self.assertEqual(response.status_code, 302)
        curriculum = Curriculum.objects.get(student=self.student2, formation=self.formation)
        self.assertIsNone(curriculum.section)
        self.assertIsNone(curriculum.rank)

    def test_admin_delete_curriculum(self):
        """Test deleting a curriculum through admin."""
        self.client.login(username='admin', password='adminpass123')
        curriculum_id = self.curriculum.id
        response = self.client.post(
            f'/admin/curriculum/curriculum/{curriculum_id}/delete/',
            {'post': 'yes'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Curriculum.objects.filter(id=curriculum_id).exists())

    def test_admin_delete_keeps_student(self):
        """Test that deleting curriculum keeps the student."""
        self.client.login(username='admin', password='adminpass123')
        student_id = self.student.id
        self.client.post(
            f'/admin/curriculum/curriculum/{self.curriculum.id}/delete/',
            {'post': 'yes'},
        )
        self.assertTrue(Student.objects.filter(id=student_id).exists())

    def test_admin_delete_keeps_formation(self):
        """Test that deleting curriculum keeps the formation."""
        self.client.login(username='admin', password='adminpass123')
        formation_id = self.formation.id
        self.client.post(
            f'/admin/curriculum/curriculum/{self.curriculum.id}/delete/',
            {'post': 'yes'},
        )
        self.assertTrue(Formation.objects.filter(id=formation_id).exists())

    # ==================== ADMIN SEARCH TESTS ====================

    def test_admin_search_by_student_first_name(self):
        """Test searching by student first name."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/?q=Mohammed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.curriculum.id))

    def test_admin_search_by_student_last_name(self):
        """Test searching by student last name."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/?q=Merzougui')
        self.assertEqual(response.status_code, 200)

    def test_admin_search_by_section(self):
        """Test searching by section."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/?q=A')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'active')

    def test_admin_search_by_status(self):
        """Test searching by status."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/?q=active')
        self.assertEqual(response.status_code, 200)

    def test_admin_search_no_results(self):
        """Test search with no matching results."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/?q=Inexistant')
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN DISPLAY TESTS ====================

    def test_admin_displays_id(self):
        """Test that admin displays curriculum ID."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertContains(response, str(self.curriculum.id))

    def test_admin_displays_status(self):
        """Test that admin displays status."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertContains(response, 'active')

    def test_admin_change_form_shows_readonly_id(self):
        """Test that change form shows the readonly ID."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/curriculum/curriculum/{self.curriculum.id}/change/')
        self.assertContains(response, str(self.curriculum.id))

    # ==================== ADMIN READONLY FIELDS TESTS ====================

    def test_readonly_id_cannot_be_changed(self):
        """Test that ID cannot be changed via admin."""
        self.client.login(username='admin', password='adminpass123')
        new_id = uuid.uuid4()
        data = {
            'id': str(new_id),
            'student': self.student.id,
            'formation': self.formation.id,
            'status': 'active',
        }
        self.client.post(f'/admin/curriculum/curriculum/{self.curriculum.id}/change/', data)
        self.curriculum.refresh_from_db()
        self.assertNotEqual(self.curriculum.id, new_id)

    def test_readonly_student_cannot_be_changed_via_form(self):
        """Test that student readonly field cannot be changed via form."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'student': str(self.student2.id),  # Attempt to change student
            'formation': self.formation.id,
            'status': 'active',
            'section': 'A',
            'group': 'G1',
        }
        self.client.post(f'/admin/curriculum/curriculum/{self.curriculum.id}/change/', data)
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.student, self.student)  # Should not have changed

    def test_readonly_status_cannot_be_changed_via_form(self):
        """Test that status readonly field cannot be changed via form."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'student': self.student.id,
            'formation': self.formation.id,
            'status': 'graduated',  # Attempt to change status
        }
        self.client.post(f'/admin/curriculum/curriculum/{self.curriculum.id}/change/', data)
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.status, 'active')  # Should not have changed

    # ==================== ADMIN VALIDATION TESTS ====================

    def test_admin_create_without_status_fails(self):
        """Test that creating without status shows an error."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'student': self.student2.id,
            'formation': self.formation.id,
        }
        response = self.client.post('/admin/curriculum/curriculum/add/', data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')

    def test_admin_create_duplicate_student_formation_fails(self):
        """Test that duplicate student+formation shows an error."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'student': self.student.id,
            'formation': self.formation.id,
            'status': 'active',
        }
        response = self.client.post('/admin/curriculum/curriculum/add/', data)
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN PERMISSIONS TESTS ====================

    def test_non_superuser_cannot_access_admin(self):
        """Test that regular user cannot access admin."""
        User.objects.create_user(username='regular', password='pass123')
        self.client.login(username='regular', password='pass123')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertIn(response.status_code, [302, 403])

    def test_staff_user_with_permissions_can_access(self):
        """Test that staff user with permissions can access admin."""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        staff_user = User.objects.create_user(
            username='staff', password='staffpass123', is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Curriculum)
        permissions = Permission.objects.filter(content_type=content_type)
        staff_user.user_permissions.set(permissions)

        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertEqual(response.status_code, 200)

    # ==================== ADMIN MULTIPLE RECORDS TESTS ====================

    def test_admin_displays_multiple_curriculums(self):
        """Test admin correctly displays multiple curriculums."""
        self.client.login(username='admin', password='adminpass123')
        Curriculum.objects.create(student=self.student2, formation=self.formation, status='graduated')
        response = self.client.get('/admin/curriculum/curriculum/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'active')
        self.assertContains(response, 'graduated')


import uuid