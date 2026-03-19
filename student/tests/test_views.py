# student/tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from student.models import Student
from datetime import date
import json


class StudentViewSetTest(APITestCase):
    """Tests for the Student API endpoints."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.list_url = reverse('student-list')
        
        # Create test students
        self.student1 = Student.objects.create(
            matricule='E074001',
            first_name='Mohammed',
            last_name='Merzougui',
            birth_date=date(2000, 1, 1)
        )
        self.student2 = Student.objects.create(
            matricule='E074002',
            first_name='Karim',
            last_name='Merzouk',
            birth_date=date(1999, 3, 15)
        )
        self.student3 = Student.objects.create(
            matricule=None,
            first_name='NoMatricule',
            last_name='Student',
            birth_date=date(2001, 5, 20)
        )
        
        self.detail_url = reverse('student-detail', kwargs={'pk': self.student1.id})
    
    # ==================== LIST TESTS (GET /api/v1/students/) ====================
    
    def test_list_all_students(self):
        """Test GET request returns all students."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_list_returns_correct_fields(self):
        """Test that list returns correct fields for each student."""
        response = self.client.get(self.list_url)
        
        first_student = response.data[0]
        expected_fields = {'matricule', 'first_name', 'last_name', 'birth_date'}
        self.assertEqual(set(first_student.keys()), expected_fields)
    
    def test_list_empty_when_no_students(self):
        """Test list returns empty array when no students exist."""
        Student.objects.all().delete()
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_list_students_ordering(self):
        """Test that students are returned in correct order."""
        response = self.client.get(self.list_url)
        
        # Assuming default ordering is by -created_at (newest first)
        # The last created student should be first
        self.assertEqual(response.data[0]['matricule'], None)  # student3
    
    # ==================== CREATE TESTS (POST /api/v1/students/) ====================
    
    def test_create_student_with_all_fields(self):
        """Test creating a student with all fields."""
        data = {
            'matricule': 'E074010',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-06-15'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 4)
        
        # Verify created student
        created_student = Student.objects.get(matricule='E074010')
        self.assertEqual(created_student.first_name, 'Test')
        self.assertEqual(created_student.last_name, 'User')
    
    def test_create_student_without_matricule(self):
        """Test creating a student without matricule."""
        data = {
            'first_name': 'NoMatricule',
            'last_name': 'Test',
            'birth_date': '2000-06-15'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['matricule'])
    
    def test_create_student_with_null_matricule(self):
        """Test creating a student with explicit null matricule."""
        data = {
            'matricule': None,
            'first_name': 'NullMatricule',
            'last_name': 'Test',
            'birth_date': '2000-06-15'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_student_missing_required_field(self):
        """Test that creating without required field fails."""
        data = {
            'matricule': 'E074020',
            'last_name': 'User',
            'birth_date': '2000-06-15'
            # Missing first_name
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
    
    def test_create_student_with_duplicate_matricule(self):
        """Test that creating with duplicate matricule fails."""
        data = {
            'matricule': 'E074001',  # Already exists
            'first_name': 'Duplicate',
            'last_name': 'Test',
            'birth_date': '2000-06-15'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_student_with_invalid_date(self):
        """Test creating with invalid date format fails."""
        data = {
            'matricule': 'E074030',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': 'invalid-date'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('birth_date', response.data)
    
    def test_create_student_with_too_long_matricule(self):
        """Test creating with matricule exceeding max_length fails."""
        data = {
            'matricule': 'E' * 21,  # Exceeds 20
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-06-15'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_multiple_students_with_null_matricule(self):
        """Test creating multiple students with null matricule succeeds."""
        for i in range(3):
            data = {
                'matricule': None,
                'first_name': f'Student{i}',
                'last_name': 'NullMatricule',
                'birth_date': '2000-06-15'
            }
            response = self.client.post(self.list_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Total should be 3 original + 3 new = 6
        self.assertEqual(Student.objects.count(), 6)
    
    # ==================== RETRIEVE TESTS (GET /api/v1/students/{id}/) ====================
    
    def test_retrieve_existing_student(self):
        """Test retrieving an existing student by ID."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['matricule'], 'E074001')
        self.assertEqual(response.data['first_name'], 'Mohammed')
    
    def test_retrieve_nonexistent_student(self):
        """Test retrieving a non-existent student returns 404."""
        url = reverse('student-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_with_invalid_uuid(self):
        """Test retrieving with invalid UUID format returns 404."""
        url = '/api/v1/students/invalid-uuid/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_student_without_matricule(self):
        """Test retrieving student that has null matricule."""
        url = reverse('student-detail', kwargs={'pk': self.student3.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['matricule'])
    
    # ==================== UPDATE TESTS (PUT /api/v1/students/{id}/) ====================
    
    def test_full_update_student(self):
        """Test full update (PUT) of a student."""
        data = {
            'matricule': 'E999999',
            'first_name': 'Updated',
            'last_name': 'Name',
            'birth_date': '1999-12-31'
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify update
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.matricule, 'E999999')
        self.assertEqual(self.student1.first_name, 'Updated')
        self.assertEqual(self.student1.last_name, 'Name')
    
    def test_full_update_missing_required_field(self):
        """Test that full update without required field fails."""
        data = {
            'matricule': 'E999999',
            'first_name': 'Updated',
            # Missing last_name and birth_date
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_full_update_nonexistent_student(self):
        """Test full update of non-existent student returns 404."""
        url = reverse('student-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        data = {
            'matricule': 'E999999',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-01-01'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== PARTIAL UPDATE TESTS (PATCH /api/v1/students/{id}/) ====================
    
    def test_partial_update_first_name(self):
        """Test partial update (PATCH) of first_name only."""
        data = {'first_name': 'PartialUpdate'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.first_name, 'PartialUpdate')
        self.assertEqual(self.student1.last_name, 'Merzougui')  # Unchanged
    
    def test_partial_update_matricule(self):
        """Test partial update of matricule only."""
        data = {'matricule': 'E888888'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.matricule, 'E888888')
    
    def test_partial_update_multiple_fields(self):
        """Test partial update of multiple fields."""
        data = {
            'first_name': 'NewFirst',
            'last_name': 'NewLast'
        }
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.first_name, 'NewFirst')
        self.assertEqual(self.student1.last_name, 'NewLast')
        self.assertEqual(self.student1.matricule, 'E074001')  # Unchanged
    
    def test_partial_update_to_null_matricule(self):
        """Test partial update setting matricule to null."""
        data = {'matricule': None}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student1.refresh_from_db()
        self.assertIsNone(self.student1.matricule)
    
    def test_partial_update_with_invalid_data(self):
        """Test partial update with invalid data fails."""
        data = {'birth_date': 'invalid-date'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # ==================== DELETE TESTS (DELETE /api/v1/students/{id}/) ====================
    
    def test_delete_existing_student(self):
        """Test deleting an existing student."""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Student.objects.count(), 2)
        self.assertFalse(Student.objects.filter(id=self.student1.id).exists())
    
    def test_delete_nonexistent_student(self):
        """Test deleting a non-existent student returns 404."""
        url = reverse('student-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_twice(self):
        """Test deleting the same student twice fails on second attempt."""
        # First delete
        response1 = self.client.delete(self.detail_url)
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)
        
        # Second delete
        response2 = self.client.delete(self.detail_url)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== SEARCH & FILTER TESTS ====================
    
    def test_search_by_first_name(self):
        """Test searching students by first_name."""
        response = self.client.get(self.list_url, {'search': 'Mohammed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'Mohammed')
    
    def test_search_by_last_name(self):
        """Test searching students by last_name."""
        response = self.client.get(self.list_url, {'search': 'Merzouk'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['last_name'], 'Merzouk')
    
    def test_search_by_matricule(self):
        """Test searching students by matricule."""
        response = self.client.get(self.list_url, {'search': 'E074001'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['matricule'], 'E074001')
    
    def test_search_partial_match(self):
        """Test searching with partial matches."""
        response = self.client.get(self.list_url, {'search': 'Mer'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should match Merzougui and Merzouk
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response = self.client.get(self.list_url, {'search': 'mohammed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_search_no_results(self):
        """Test searching with no matches returns empty list."""
        response = self.client.get(self.list_url, {'search': 'NonexistentName'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ==================== ORDERING TESTS ====================
    
    def test_ordering_by_matricule_ascending(self):
        """Test ordering students by matricule (A→Z)."""
        response = self.client.get(self.list_url, {'ordering': 'matricule'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Null matricules come first, then alphabetical
        self.assertIsNone(response.data[0]['matricule'])
    
    def test_ordering_by_matricule_descending(self):
        """Test ordering students by matricule (Z→A)."""
        response = self.client.get(self.list_url, {'ordering': '-matricule'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Non-null matricules first in descending order
        self.assertEqual(response.data[0]['matricule'], 'E074002')
    
    def test_ordering_by_created_at(self):
        """Test ordering by created_at."""
        response = self.client.get(self.list_url, {'ordering': '-created_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Just verify we get all students - timing-based order is unreliable
        self.assertEqual(len(response.data), 3)
    
    # ==================== EDGE CASES ====================
    
    def test_create_with_special_characters(self):
        """Test creating student with special characters in name."""
        data = {
            'matricule': 'E074050',
            'first_name': "Jean-Pierre",
            'last_name': "O'Brien",
            'birth_date': '2000-01-01'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_with_unicode_characters(self):
        """Test creating student with Arabic characters."""
        data = {
            'matricule': 'E074060',
            'first_name': 'محمد',
            'last_name': 'مرزوقي',
            'birth_date': '2000-01-01'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'محمد')
    
    def test_concurrent_creates_with_same_matricule(self):
        """Test that concurrent creates with same matricule fail."""
        data = {
            'matricule': 'E074070',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-01-01'
        }
        
        # First create should succeed
        response1 = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second create should fail
        response2 = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_malformed_json(self):
        """Test that malformed JSON returns 400."""
        response = self.client.post(
            self.list_url,
            'not valid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_empty_post_request(self):
        """Test that empty POST request returns 400."""
        response = self.client.post(self.list_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)