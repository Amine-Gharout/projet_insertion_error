# student/tests/test_admin.py
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from student.models import Student
from student.admin import StudentAdmin
from datetime import date


class StudentAdminTest(TestCase):
    """Tests for the Student Admin interface."""
    
    def setUp(self):
        """Set up admin site and test data."""
        self.site = AdminSite()
        self.admin = StudentAdmin(Student, self.site)
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test student
        self.student = Student.objects.create(
            matricule='E074001',
            first_name='Mohammed',
            last_name='Merzougui',
            birth_date=date(2000, 1, 1)
        )
        
        self.client = Client()
    
    # ==================== ADMIN CONFIGURATION TESTS ====================
    
    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        expected_fields = ['matricule', 'full_name', 'birth_date', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        expected_fields = ['matricule', 'first_name', 'last_name']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        expected_fields = ['created_at', 'birth_date']
        self.assertEqual(list(self.admin.list_filter), expected_fields)
    
    def test_ordering(self):
        """Test default ordering."""
        expected_ordering = ['-created_at']
        self.assertEqual(list(self.admin.ordering), expected_ordering)
    
    def test_readonly_fields(self):
        """Test readonly fields."""
        expected_readonly = ['id', 'created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_readonly)
    
    # ==================== CUSTOM METHOD TESTS ====================
    
    def test_full_name_method(self):
        """Test full_name custom method."""
        result = self.admin.full_name(self.student)
        self.assertEqual(result, 'Mohammed Merzougui')
    
    def test_full_name_with_different_names(self):
        """Test full_name with various name combinations."""
        test_cases = [
            ('Jean', 'Pierre', 'Jean Pierre'),
            ('محمد', 'علي', 'محمد علي'),
            ('A', 'B', 'A B'),
        ]
        
        for first, last, expected in test_cases:
            student = Student.objects.create(
                first_name=first,
                last_name=last,
                birth_date=date(2000, 1, 1)
            )
            result = self.admin.full_name(student)
            self.assertEqual(result, expected)
    
    # ==================== ADMIN INTERFACE TESTS ====================
    
    def test_admin_login_required(self):
        """Test that admin interface requires authentication."""
        response = self.client.get('/admin/student/student/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_admin_access_with_superuser(self):
        """Test admin access with superuser credentials."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/student/student/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_changelist_displays_students(self):
        """Test that changelist displays students."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/student/student/')
        
        self.assertContains(response, 'E074001')
        self.assertContains(response, 'Mohammed')
        self.assertContains(response, 'Merzougui')
    
    def test_admin_search_functionality(self):
        """Test admin search functionality."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/student/student/?q=Mohammed')
        
        self.assertContains(response, 'Mohammed')
    
    def test_admin_add_student(self):
        """Test adding a student through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'matricule': 'E074010',
            'first_name': 'AdminTest',
            'last_name': 'User',
            'birth_date': '2000-01-01'
        }
        response = self.client.post('/admin/student/student/add/', data)
        
        # Check if student was created
        self.assertTrue(Student.objects.filter(matricule='E074010').exists())
    
    def test_admin_edit_student(self):
        """Test editing a student through admin."""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'matricule': 'E074001',
            'first_name': 'Updated',
            'last_name': 'Name',
            'birth_date': '2000-01-01'
        }
        response = self.client.post(
            f'/admin/student/student/{self.student.id}/change/',
            data
        )
        
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Updated')
    
    def test_admin_delete_student(self):
        """Test deleting a student through admin."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(
            f'/admin/student/student/{self.student.id}/delete/',
            {'post': 'yes'}
        )
        
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())
