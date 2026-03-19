# program/tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from program.models import Program
import json


class ProgramViewSetTest(APITestCase):
    """Tests for the Program API endpoints."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.list_url = reverse('program-list')
        
        # Create test programs
        self.program1 = Program.objects.create(
            title='Informatique',
            code='INFO101',
            description='Programme en informatique',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        self.program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            description='Programme en mathématiques',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        self.program3 = Program.objects.create(
            title='Génie Logiciel',
            code='GL301',
            description=None,
            cycle='Master',
            diploma='Master en Génie Logiciel'
        )
        
        self.detail_url = reverse('program-detail', kwargs={'pk': self.program1.id})
    
    # ==================== LIST TESTS (GET /api/v1/Programs/) ====================
    
    def test_list_all_programs(self):
        """Test GET request returns all programs."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_list_returns_correct_fields(self):
        """Test that list returns correct fields for each program."""
        response = self.client.get(self.list_url)
        
        first_program = response.data[0]
        expected_fields = {'title', 'code', 'description', 'cycle', 'diploma'}
        self.assertEqual(set(first_program.keys()), expected_fields)
    
    def test_list_empty_when_no_programs(self):
        """Test list returns empty array when no programs exist."""
        Program.objects.all().delete()
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_list_programs_ordering_by_title(self):
        """Test that programs are returned ordered by title."""
        response = self.client.get(self.list_url)
        
        # Default ordering is by title
        titles = [p['title'] for p in response.data]
        self.assertEqual(titles, sorted(titles))
    
    # ==================== CREATE TESTS (POST /api/v1/Programs/) ====================
    
    def test_create_program_with_all_fields(self):
        """Test creating a program with all fields."""
        data = {
            'title': 'Réseaux Informatiques',
            'code': 'NET401',
            'description': 'Programme de réseaux',
            'cycle': 'Licence',
            'diploma': 'Licence en Réseaux'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Program.objects.count(), 4)
        
        # Verify created program
        created_program = Program.objects.get(code='NET401')
        self.assertEqual(created_program.title, 'Réseaux Informatiques')
        self.assertEqual(created_program.description, 'Programme de réseaux')
        self.assertEqual(created_program.cycle, 'Licence')
    
    def test_create_program_without_description(self):
        """Test creating a program without description."""
        data = {
            'title': 'Systèmes',
            'code': 'SYS501',
            'cycle': 'Master',
            'diploma': 'Master en Systèmes'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['description'])
    
    def test_create_program_with_null_description(self):
        """Test creating a program with explicit null description."""
        data = {
            'title': 'Sécurité',
            'code': 'SEC601',
            'description': None,
            'cycle': 'Master',
            'diploma': 'Master en Sécurité'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_program_missing_title(self):
        """Test that creating without title fails."""
        data = {
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
    
    def test_create_program_missing_code(self):
        """Test that creating without code fails."""
        data = {
            'title': 'Test Program',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
    
    def test_create_program_missing_cycle(self):
        """Test that creating without cycle fails."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'diploma': 'Test Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cycle', response.data)
    
    def test_create_program_missing_diploma(self):
        """Test that creating without diploma fails."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'Licence'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('diploma', response.data)
    
    def test_create_program_with_duplicate_title(self):
        """Test that creating with duplicate title fails."""
        data = {
            'title': 'Informatique',  # Already exists
            'code': 'DIFF001',
            'cycle': 'Master',
            'diploma': 'Master en Informatique'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_program_with_duplicate_code(self):
        """Test that creating with duplicate code fails."""
        data = {
            'title': 'Different Program',
            'code': 'INFO101',  # Already exists
            'cycle': 'Master',
            'diploma': 'Master Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_program_with_empty_title(self):
        """Test creating with empty title fails."""
        data = {
            'title': '',
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_program_with_empty_code(self):
        """Test creating with empty code fails."""
        data = {
            'title': 'Test Program',
            'code': '',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # ==================== RETRIEVE TESTS (GET /api/v1/Programs/{id}/) ====================
    
    def test_retrieve_program(self):
        """Test retrieving a single program by ID."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Informatique')
        self.assertEqual(response.data['code'], 'INFO101')
        self.assertEqual(response.data['cycle'], 'Licence')
        self.assertEqual(response.data['diploma'], 'Licence en Informatique')
    
    def test_retrieve_nonexistent_program(self):
        """Test retrieving a non-existent program returns 404."""
        import uuid
        nonexistent_url = reverse('program-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_program_with_null_description(self):
        """Test retrieving a program with null description."""
        detail_url = reverse('program-detail', kwargs={'pk': self.program3.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['description'])
    
    # ==================== UPDATE TESTS (PUT /api/v1/Programs/{id}/) ====================
    
    def test_update_program_all_fields(self):
        """Test full update of a program."""
        data = {
            'title': 'Informatique Avancée',
            'code': 'INFO102',
            'description': 'Programme avancé',
            'cycle': 'Master',
            'diploma': 'Master en Informatique'
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Informatique Avancée')
        self.assertEqual(response.data['code'], 'INFO102')
        self.assertEqual(response.data['cycle'], 'Master')
    
    def test_update_program_title_only(self):
        """Test updating only program title (full update requires all fields)."""
        data = {
            'title': 'Nouveau Titre',
            'code': 'INFO101',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Nouveau Titre')
    
    def test_update_with_duplicate_title_fails(self):
        """Test that updating to existing title fails."""
        data = {
            'title': 'Mathématiques',  # Already exists (program2)
            'code': 'INFO101',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_with_duplicate_code_fails(self):
        """Test that updating to existing code fails."""
        data = {
            'title': 'Test',
            'code': 'MATH201',  # Already exists (program2)
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_nonexistent_program(self):
        """Test updating non-existent program returns 404."""
        import uuid
        nonexistent_url = reverse('program-detail', kwargs={'pk': uuid.uuid4()})
        data = {
            'title': 'Test',
            'code': 'TEST',
            'cycle': 'Licence',
            'diploma': 'Test'
        }
        response = self.client.put(nonexistent_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== PARTIAL UPDATE TESTS (PATCH /api/v1/Programs/{id}/) ====================
    
    def test_partial_update_title(self):
        """Test partial update of title only."""
        data = {'title': 'Informatique Modifiée'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Informatique Modifiée')
        self.assertEqual(response.data['code'], 'INFO101')  # Unchanged
    
    def test_partial_update_code(self):
        """Test partial update of code only."""
        data = {'code': 'INFO999'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'INFO999')
        self.assertEqual(response.data['title'], 'Informatique')  # Unchanged
    
    def test_partial_update_description(self):
        """Test partial update of description only."""
        data = {'description': 'Nouvelle description'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Nouvelle description')
    
    def test_partial_update_cycle(self):
        """Test partial update of cycle only."""
        data = {'cycle': 'Doctorat'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cycle'], 'Doctorat')
    
    def test_partial_update_diploma(self):
        """Test partial update of diploma only."""
        data = {'diploma': 'Master en Informatique'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diploma'], 'Master en Informatique')
    
    def test_partial_update_clear_description(self):
        """Test partial update to clear description."""
        data = {'description': None}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['description'])
    
    # ==================== DELETE TESTS (DELETE /api/v1/Programs/{id}/) ====================
    
    def test_delete_program(self):
        """Test deleting a program."""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Program.objects.count(), 2)
    
    def test_delete_nonexistent_program(self):
        """Test deleting non-existent program returns 404."""
        import uuid
        nonexistent_url = reverse('program-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_allows_title_reuse(self):
        """Test that deleted program's title can be reused."""
        title = self.program1.title
        self.client.delete(self.detail_url)
        
        # Create new program with same title
        data = {
            'title': title,
            'code': 'NEW001',
            'cycle': 'Master',
            'diploma': 'Master Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_allows_code_reuse(self):
        """Test that deleted program's code can be reused."""
        code = self.program1.code
        self.client.delete(self.detail_url)
        
        # Create new program with same code
        data = {
            'title': 'New Program',
            'code': code,
            'cycle': 'Master',
            'diploma': 'Master Diploma'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    # ==================== SEARCH/FILTER TESTS ====================
    
    def test_search_by_title(self):
        """Test searching programs by title."""
        response = self.client.get(self.list_url, {'search': 'Informatique'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Informatique')
    
    def test_search_by_code(self):
        """Test searching programs by code."""
        response = self.client.get(self.list_url, {'search': 'MATH201'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'MATH201')
    
    def test_search_by_cycle(self):
        """Test searching programs by cycle."""
        response = self.client.get(self.list_url, {'search': 'Master'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_search_by_diploma(self):
        """Test searching programs by diploma."""
        response = self.client.get(self.list_url, {'search': 'Licence en Informatique'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_search_partial_title(self):
        """Test searching with partial title."""
        response = self.client.get(self.list_url, {'search': 'Info'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.list_url, {'search': 'NonExistent'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ==================== ORDERING TESTS ====================
    
    def test_ordering_by_title_ascending(self):
        """Test ordering programs by title ascending."""
        response = self.client.get(self.list_url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in response.data]
        self.assertEqual(titles, sorted(titles))
    
    def test_ordering_by_title_descending(self):
        """Test ordering programs by title descending."""
        response = self.client.get(self.list_url, {'ordering': '-title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in response.data]
        self.assertEqual(titles, sorted(titles, reverse=True))
    
    def test_ordering_by_code_ascending(self):
        """Test ordering programs by code ascending."""
        response = self.client.get(self.list_url, {'ordering': 'code'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [p['code'] for p in response.data]
        self.assertEqual(codes, sorted(codes))
    
    def test_ordering_by_code_descending(self):
        """Test ordering programs by code descending."""
        response = self.client.get(self.list_url, {'ordering': '-code'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [p['code'] for p in response.data]
        self.assertEqual(codes, sorted(codes, reverse=True))
    
    def test_ordering_by_cycle(self):
        """Test ordering programs by cycle."""
        response = self.client.get(self.list_url, {'ordering': 'cycle'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cycles = [p['cycle'] for p in response.data]
        self.assertEqual(cycles, sorted(cycles))
    
    def test_ordering_by_diploma(self):
        """Test ordering programs by diploma."""
        response = self.client.get(self.list_url, {'ordering': 'diploma'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        diplomas = [p['diploma'] for p in response.data]
        self.assertEqual(diplomas, sorted(diplomas))
    
    # ==================== EDGE CASES ====================
    
    def test_create_with_special_characters(self):
        """Test creating program with special characters."""
        data = {
            'title': 'C++ & C# Programming',
            'code': 'CPP001',
            'description': 'Learn <C++> & C#',
            'cycle': 'Licence',
            'diploma': 'Licence en Programmation'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'C++ & C# Programming')
    
    def test_create_with_unicode(self):
        """Test creating program with unicode characters."""
        data = {
            'title': 'Mathématiques العربية',
            'code': 'MATH001',
            'description': 'Description éèê',
            'cycle': 'Licence',
            'diploma': 'Licence en Mathématiques'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_request_with_invalid_json(self):
        """Test handling of invalid JSON in request body."""
        response = self.client.post(
            self.list_url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_with_extra_fields_ignored(self):
        """Test that extra fields in request are ignored."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma',
            'extra_field': 'should be ignored',
            'another_extra': 123
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('extra_field', response.data)
    
    def test_combined_search_and_ordering(self):
        """Test combining search and ordering."""
        response = self.client.get(
            self.list_url,
            {'search': 'Master', 'ordering': '-title'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 1:
            titles = [p['title'] for p in response.data]
            self.assertEqual(titles, sorted(titles, reverse=True))
