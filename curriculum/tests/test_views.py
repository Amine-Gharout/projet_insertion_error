from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from curriculum.models import Curriculum
from student.models import Student
from formation.models import Formation
import uuid


class CurriculumViewSetTest(APITestCase):
    """Tests for the Curriculum API endpoints."""

    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.list_url = reverse('curriculum-list')

        self.student1 = Student.objects.create(first_name='Mohammed', last_name='Merzougui', matricule='E074001')
        self.student2 = Student.objects.create(first_name='Karim', last_name='Merzouk', matricule='E074002')
        self.student3 = Student.objects.create(first_name='Amine', last_name='Gharout', matricule='E074003')

        self.formation1 = Formation.objects.create(name='Promotion 2024', year=2024)
        self.formation2 = Formation.objects.create(name='Promotion 2025', year=2025)

        self.curriculum1 = Curriculum.objects.create(
            student=self.student1, formation=self.formation1,
            section='A', group='G1', status='active', rank=1,
            moyenne_finale=14.5, moyenne_rachat=12.0, moyenne_concours=15.0,
        )
        self.curriculum2 = Curriculum.objects.create(
            student=self.student2, formation=self.formation1,
            section='A', group='G2', status='active', rank=2,
            moyenne_finale=13.0,
        )
        self.curriculum3 = Curriculum.objects.create(
            student=self.student3, formation=self.formation2,
            section='B', status='graduated', rank=1,
        )

        self.detail_url = reverse('curriculum-detail', kwargs={'pk': self.curriculum1.id})

    # ==================== LIST TESTS ====================

    def test_list_all_curriculums(self):
        """Test GET returns all curriculums."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_returns_correct_fields(self):
        """Test list returns all expected fields."""
        response = self.client.get(self.list_url)
        expected_fields = {
            'id', 'section', 'group', 'student', 'formation',
            'moyenne_rachat', 'moyenne_finale', 'moyenne_concours',
            'status', 'rank', 'created_at', 'updated_at'
        }
        self.assertEqual(set(response.data[0].keys()), expected_fields)

    def test_list_empty_when_no_curriculums(self):
        """Test list returns empty array when no curriculums exist."""
        Curriculum.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ==================== CREATE TESTS ====================

    def test_create_curriculum_with_all_fields(self):
        """Test creating a curriculum with all fields."""
        data = {
            'student': str(self.student1.id),
            'formation': str(self.formation2.id),
            'section': 'C',
            'group': 'G3',
            'status': 'active',
            'rank': 3,
            'moyenne_finale': 15.0,
            'moyenne_rachat': 13.0,
            'moyenne_concours': 16.0,
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Curriculum.objects.count(), 4)

    def test_create_curriculum_required_fields_only(self):
        """Test creating with only required fields."""
        new_student = Student.objects.create(first_name='New', last_name='Student', matricule='E074004')
        data = {
            'student': str(new_student.id),
            'formation': str(self.formation1.id),
            'status': 'active',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['section'])
        self.assertIsNone(response.data['rank'])

    def test_create_missing_student(self):
        """Test that creating without student fails."""
        data = {'formation': str(self.formation2.id), 'status': 'active'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student', response.data)

    def test_create_missing_formation(self):
        """Test that creating without formation fails."""
        data = {'student': str(self.student1.id), 'status': 'active'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('formation', response.data)

    def test_create_missing_status(self):
        """Test that creating without status fails."""
        data = {'student': str(self.student1.id), 'formation': str(self.formation2.id)}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_create_duplicate_student_formation_fails(self):
        """Test that duplicate student+formation combination fails."""
        data = {
            'student': str(self.student1.id),
            'formation': str(self.formation1.id),  # Already exists
            'status': 'active',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_nonexistent_student(self):
        """Test creating with non-existent student fails."""
        data = {'student': str(uuid.uuid4()), 'formation': str(self.formation2.id), 'status': 'active'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_nonexistent_formation(self):
        """Test creating with non-existent formation fails."""
        data = {'student': str(self.student1.id), 'formation': str(uuid.uuid4()), 'status': 'active'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==================== RETRIEVE TESTS ====================

    def test_retrieve_curriculum(self):
        """Test retrieving a single curriculum."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'active')
        self.assertEqual(response.data['section'], 'A')
        self.assertEqual(response.data['moyenne_finale'], 14.5)

    def test_retrieve_nonexistent_curriculum(self):
        """Test retrieving non-existent curriculum returns 404."""
        url = reverse('curriculum-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== UPDATE TESTS ====================

    def test_full_update_curriculum(self):
        """Test full update of a curriculum."""
        data = {
            'student': str(self.student1.id),
            'formation': str(self.formation1.id),
            'section': 'D',
            'group': 'G4',
            'status': 'graduated',
            'rank': 1,
            'moyenne_finale': 17.0,
            'moyenne_rachat': None,
            'moyenne_concours': 18.0,
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'graduated')
        self.assertEqual(response.data['section'], 'D')

    def test_update_nonexistent_curriculum(self):
        """Test updating non-existent curriculum returns 404."""
        url = reverse('curriculum-detail', kwargs={'pk': uuid.uuid4()})
        data = {'student': str(self.student1.id), 'formation': str(self.formation1.id), 'status': 'active'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== PARTIAL UPDATE TESTS ====================

    def test_partial_update_status(self):
        """Test partial update of status."""
        response = self.client.patch(self.detail_url, {'status': 'inactive'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'inactive')
        self.assertEqual(response.data['section'], 'A')  # Unchanged

    def test_partial_update_rank(self):
        """Test partial update of rank."""
        response = self.client.patch(self.detail_url, {'rank': 99}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rank'], 99)

    def test_partial_update_moyenne_finale(self):
        """Test partial update of moyenne_finale."""
        response = self.client.patch(self.detail_url, {'moyenne_finale': 19.5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['moyenne_finale'], 19.5)

    def test_partial_update_set_section_null(self):
        """Test partial update setting section to null."""
        response = self.client.patch(self.detail_url, {'section': None}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['section'])

    def test_partial_update_set_rank_null(self):
        """Test partial update setting rank to null."""
        response = self.client.patch(self.detail_url, {'rank': None}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['rank'])

    # ==================== DELETE TESTS ====================

    def test_delete_curriculum(self):
        """Test deleting a curriculum."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Curriculum.objects.count(), 2)

    def test_delete_nonexistent_curriculum(self):
        """Test deleting non-existent curriculum returns 404."""
        url = reverse('curriculum-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_does_not_delete_student(self):
        """Test deleting curriculum does not delete student."""
        student_id = self.student1.id
        self.client.delete(self.detail_url)
        self.assertTrue(Student.objects.filter(id=student_id).exists())

    def test_delete_does_not_delete_formation(self):
        """Test deleting curriculum does not delete formation."""
        formation_id = self.formation1.id
        self.client.delete(self.detail_url)
        self.assertTrue(Formation.objects.filter(id=formation_id).exists())

    # ==================== SEARCH TESTS ====================

    def test_search_by_student_first_name(self):
        """Test searching by student first name."""
        response = self.client.get(self.list_url, {'search': 'Mohammed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student'], self.student1.id)

    def test_search_by_student_last_name(self):
        """Test searching by student last name."""
        response = self.client.get(self.list_url, {'search': 'Merzouk'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_search_by_section(self):
        """Test searching by section."""
        response = self.client.get(self.list_url, {'search': 'A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_search_by_status(self):
        """Test searching by status."""
        response = self.client.get(self.list_url, {'search': 'graduated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_formation_name(self):
        """Test searching by formation name."""
        response = self.client.get(self.list_url, {'search': 'Promotion 2024'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.list_url, {'search': 'Inexistant'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ==================== ORDERING TESTS ====================

    def test_ordering_by_rank_ascending(self):
        """Test ordering by rank ascending."""
        response = self.client.get(self.list_url, {'ordering': 'rank'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ranks = [c['rank'] for c in response.data if c['rank'] is not None]
        self.assertEqual(ranks, sorted(ranks))

    def test_ordering_by_rank_descending(self):
        """Test ordering by rank descending."""
        response = self.client.get(self.list_url, {'ordering': '-rank'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ranks = [c['rank'] for c in response.data if c['rank'] is not None]
        self.assertEqual(ranks, sorted(ranks, reverse=True))

    def test_ordering_by_moyenne_finale_ascending(self):
        """Test ordering by moyenne_finale ascending."""
        response = self.client.get(self.list_url, {'ordering': 'moyenne_finale'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        moyennes = [c['moyenne_finale'] for c in response.data if c['moyenne_finale'] is not None]
        self.assertEqual(moyennes, sorted(moyennes))

    def test_ordering_by_moyenne_finale_descending(self):
        """Test ordering by moyenne_finale descending."""
        response = self.client.get(self.list_url, {'ordering': '-moyenne_finale'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        moyennes = [c['moyenne_finale'] for c in response.data if c['moyenne_finale'] is not None]
        self.assertEqual(moyennes, sorted(moyennes, reverse=True))

    def test_ordering_by_moyenne_concours(self):
        """Test ordering by moyenne_concours."""
        response = self.client.get(self.list_url, {'ordering': 'moyenne_concours'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_ordering_by_moyenne_rachat(self):
        """Test ordering by moyenne_rachat."""
        response = self.client.get(self.list_url, {'ordering': 'moyenne_rachat'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    # ==================== EDGE CASES ====================

    def test_invalid_json_body(self):
        """Test handling of invalid JSON body."""
        response = self.client.post(self.list_url, data='invalid', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extra_fields_are_ignored(self):
        """Test that extra fields in request are ignored."""
        new_student = Student.objects.create(first_name='Extra', last_name='Test', matricule='E074005')
        data = {
            'student': str(new_student.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'extra_field': 'ignored',
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('extra_field', response.data)

    def test_combined_search_and_ordering(self):
        """Test combining search and ordering."""
        response = self.client.get(self.list_url, {'search': 'active', 'ordering': '-rank'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 1:
            ranks = [c['rank'] for c in response.data if c['rank'] is not None]
            self.assertEqual(ranks, sorted(ranks, reverse=True))