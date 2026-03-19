# formation/tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from formation.models import Formation
from program.models import Program
import json


class FormationViewSetTest(APITestCase):
    """Tests for the Formation API endpoints."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.list_url = reverse('formation-list')
        
        # Create test programs
        self.program1 = Program.objects.create(
            title='Informatique',
            code='INFO101',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        self.program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        
        # Create test formations
        self.formation1 = Formation.objects.create(
            name='Promotion 2024',
            year=2024,
            program=self.program1
        )
        self.formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program1
        )
        self.formation3 = Formation.objects.create(
            name='Math Promo 2024',
            year=2024,
            program=self.program2
        )
        
        self.detail_url = reverse('formation-detail', kwargs={'pk': self.formation1.id})
    
    # ==================== LIST TESTS (GET /api/v1/Formations/) ====================
    
    def test_list_all_formations(self):
        """Test GET request returns all formations."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_list_returns_correct_fields(self):
        """Test that list returns correct fields for each formation."""
        response = self.client.get(self.list_url)
        
        first_formation = response.data[0]
        expected_fields = {'name', 'year', 'program'}
        self.assertEqual(set(first_formation.keys()), expected_fields)
    
    def test_list_empty_when_no_formations(self):
        """Test list returns empty array when no formations exist."""
        Formation.objects.all().delete()
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_list_formations_ordering_by_year(self):
        """Test that formations are returned ordered by year."""
        response = self.client.get(self.list_url)
        
        # Default ordering is by year
        years = [f['year'] for f in response.data]
        self.assertEqual(years, sorted(years))
    
    # ==================== CREATE TESTS (POST /api/v1/Formations/) ====================
    
    def test_create_formation_with_all_fields(self):
        """Test creating a formation with all fields."""
        data = {
            'name': 'Promotion 2026',
            'year': 2026,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Formation.objects.count(), 4)
        
        # Verify created formation
        created_formation = Formation.objects.get(name='Promotion 2026')
        self.assertEqual(created_formation.year, 2026)
        self.assertEqual(created_formation.program, self.program1)
    
    def test_create_formation_missing_name(self):
        """Test that creating without name fails."""
        data = {
            'year': 2024,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_formation_missing_year(self):
        """Test that creating without year fails."""
        data = {
            'name': 'Test Formation',
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', response.data)
    
    def test_create_formation_missing_program(self):
        """Test that creating without program fails."""
        data = {
            'name': 'Test Formation',
            'year': 2024
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('program', response.data)
    
    def test_create_formation_with_empty_name(self):
        """Test creating with empty name fails."""
        data = {
            'name': '',
            'year': 2024,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_formation_with_nonexistent_program(self):
        """Test creating with nonexistent program fails."""
        import uuid
        data = {
            'name': 'Test Formation',
            'year': 2024,
            'program': str(uuid.uuid4())
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_multiple_formations_same_program(self):
        """Test creating multiple formations for same program."""
        data1 = {
            'name': 'Formation A',
            'year': 2026,
            'program': str(self.program1.id)
        }
        data2 = {
            'name': 'Formation B',
            'year': 2027,
            'program': str(self.program1.id)
        }
        
        response1 = self.client.post(self.list_url, data1, format='json')
        response2 = self.client.post(self.list_url, data2, format='json')
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Both should belong to same program
        formations = Formation.objects.filter(program=self.program1)
        self.assertGreaterEqual(formations.count(), 4)
    
    # ==================== RETRIEVE TESTS (GET /api/v1/Formations/{id}/) ====================
    
    def test_retrieve_formation(self):
        """Test retrieving a single formation by ID."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Promotion 2024')
        self.assertEqual(response.data['year'], 2024)
        self.assertEqual(response.data['program'], self.program1.id)
    
    def test_retrieve_nonexistent_formation(self):
        """Test retrieving a non-existent formation returns 404."""
        import uuid
        nonexistent_url = reverse('formation-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== UPDATE TESTS (PUT /api/v1/Formations/{id}/) ====================
    
    def test_update_formation_all_fields(self):
        """Test full update of a formation."""
        data = {
            'name': 'Promotion 2024 - Updated',
            'year': 2024,
            'program': str(self.program2.id)
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Promotion 2024 - Updated')
        self.assertEqual(response.data['program'], self.program2.id)
    
    def test_update_formation_name_only(self):
        """Test updating only formation name (full update requires all fields)."""
        data = {
            'name': 'Nouveau Nom',
            'year': 2024,
            'program': str(self.program1.id)
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Nouveau Nom')
    
    def test_update_nonexistent_formation(self):
        """Test updating non-existent formation returns 404."""
        import uuid
        nonexistent_url = reverse('formation-detail', kwargs={'pk': uuid.uuid4()})
        data = {
            'name': 'Test',
            'year': 2024,
            'program': str(self.program1.id)
        }
        response = self.client.put(nonexistent_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== PARTIAL UPDATE TESTS (PATCH /api/v1/Formations/{id}/) ====================
    
    def test_partial_update_name(self):
        """Test partial update of name only."""
        data = {'name': 'Formation Modifiée'}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Formation Modifiée')
        self.assertEqual(response.data['year'], 2024)  # Unchanged
    
    def test_partial_update_year(self):
        """Test partial update of year only."""
        data = {'year': 2025}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['year'], 2025)
        self.assertEqual(response.data['name'], 'Promotion 2024')  # Unchanged
    
    def test_partial_update_program(self):
        """Test partial update of program only."""
        data = {'program': str(self.program2.id)}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['program'], self.program2.id)
    
    # ==================== DELETE TESTS (DELETE /api/v1/Formations/{id}/) ====================
    
    def test_delete_formation(self):
        """Test deleting a formation."""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Formation.objects.count(), 2)
    
    def test_delete_nonexistent_formation(self):
        """Test deleting non-existent formation returns 404."""
        import uuid
        nonexistent_url = reverse('formation-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_formation_does_not_delete_program(self):
        """Test that deleting formation doesn't delete the program."""
        program_id = self.program1.id
        self.client.delete(self.detail_url)
        
        # Program should still exist
        self.assertTrue(Program.objects.filter(id=program_id).exists())
    
    # ==================== SEARCH/FILTER TESTS ====================
    
    def test_search_by_name(self):
        """Test searching formations by name."""
        response = self.client.get(self.list_url, {'search': 'Promotion 2024'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertTrue(any('Promotion 2024' in f['name'] for f in response.data))
    
    def test_search_partial_name(self):
        """Test searching with partial name."""
        response = self.client.get(self.list_url, {'search': 'Promo'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_search_by_year(self):
        """Test searching formations by year."""
        response = self.client.get(self.list_url, {'search': '2024'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.list_url, {'search': 'NonExistent'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ==================== ORDERING TESTS ====================
    
    def test_ordering_by_year_ascending(self):
        """Test ordering formations by year ascending."""
        response = self.client.get(self.list_url, {'ordering': 'year'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [f['year'] for f in response.data]
        self.assertEqual(years, sorted(years))
    
    def test_ordering_by_year_descending(self):
        """Test ordering formations by year descending."""
        response = self.client.get(self.list_url, {'ordering': '-year'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [f['year'] for f in response.data]
        self.assertEqual(years, sorted(years, reverse=True))
    
    def test_ordering_by_name_ascending(self):
        """Test ordering formations by name ascending."""
        response = self.client.get(self.list_url, {'ordering': 'name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [f['name'] for f in response.data]
        self.assertEqual(names, sorted(names))
    
    def test_ordering_by_name_descending(self):
        """Test ordering formations by name descending."""
        response = self.client.get(self.list_url, {'ordering': '-name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [f['name'] for f in response.data]
        self.assertEqual(names, sorted(names, reverse=True))
    
    def test_ordering_by_created_at(self):
        """Test ordering formations by created_at."""
        response = self.client.get(self.list_url, {'ordering': 'created_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return in chronological order
        self.assertEqual(len(response.data), 3)
    
    # ==================== EDGE CASES ====================
    
    def test_create_with_special_characters(self):
        """Test creating formation with special characters."""
        data = {
            'name': 'Promotion 2024 - Spéciale & Avancée',
            'year': 2024,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Promotion 2024 - Spéciale & Avancée')
    
    def test_create_with_unicode(self):
        """Test creating formation with unicode characters."""
        data = {
            'name': 'Promotion العربية 中文',
            'year': 2024,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_with_negative_year(self):
        """Test creating formation with negative year."""
        data = {
            'name': 'Historical Formation',
            'year': -500,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['year'], -500)
    
    def test_create_with_large_year(self):
        """Test creating formation with large year value."""
        data = {
            'name': 'Future Formation',
            'year': 9999,
            'program': str(self.program1.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['year'], 9999)
    
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
            'name': 'Test Formation',
            'year': 2024,
            'program': str(self.program1.id),
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
            {'search': '2024', 'ordering': '-name'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 1:
            names = [f['name'] for f in response.data]
            self.assertEqual(names, sorted(names, reverse=True))
    
    # ==================== RELATIONSHIP TESTS ====================
    
    def test_list_formations_by_program(self):
        """Test listing formations filtered by program."""
        # Get formations for program1
        formations_prog1 = Formation.objects.filter(program=self.program1)
        self.assertGreaterEqual(formations_prog1.count(), 2)
        
        # Get formations for program2
        formations_prog2 = Formation.objects.filter(program=self.program2)
        self.assertEqual(formations_prog2.count(), 1)
    
    def test_create_formation_verifies_program_exists(self):
        """Test that API verifies program exists before creating formation."""
        import uuid
        data = {
            'name': 'Test Formation',
            'year': 2024,
            'program': str(uuid.uuid4())  # Non-existent program
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('program', response.data)
