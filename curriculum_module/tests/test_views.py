# curriculum_module/tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from curriculum_module.models import CurriculumModule
from formation.models import Formation
from program.models import Program
from module.models import Module


class CurriculumModuleViewSetTest(APITestCase):
    """Tests for the CurriculumModule API endpoints."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = APIClient()
        self.list_url = reverse('curriculummodule-list')
        
        # Create test program
        self.program = Program.objects.create(
            title='Informatique',
            code='INFO101',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        
        # Create test formations
        self.formation1 = Formation.objects.create(
            name='Promotion 2024',
            year=2024,
            program=self.program
        )
        self.formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
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
        self.module3 = Module.objects.create(
            name='Réseaux',
            code='NET301'
        )
        
        # Create test curriculum modules
        self.cm1 = CurriculumModule.objects.create(
            formation=self.formation1,
            module=self.module1,
            coefficient=3
        )
        self.cm2 = CurriculumModule.objects.create(
            formation=self.formation1,
            module=self.module2,
            coefficient=2
        )
        self.cm3 = CurriculumModule.objects.create(
            formation=self.formation2,
            module=self.module1,
            coefficient=4
        )
        
        self.detail_url = reverse('curriculummodule-detail', kwargs={'pk': self.cm1.id})
    
    # ==================== LIST TESTS ====================
    
    def test_list_all_curriculum_modules(self):
        """Test GET request returns all curriculum modules."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_list_returns_correct_fields(self):
        """Test that list returns correct fields."""
        response = self.client.get(self.list_url)
        
        first_item = response.data[0]
        expected_fields = {'id', 'formation', 'module', 'coefficient'}
        self.assertEqual(set(first_item.keys()), expected_fields)
    
    def test_list_empty_when_no_curriculum_modules(self):
        """Test list returns empty array when no curriculum modules exist."""
        CurriculumModule.objects.all().delete()
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ==================== CREATE TESTS ====================
    
    def test_create_curriculum_module_with_all_fields(self):
        """Test creating a curriculum module with all fields."""
        data = {
            'formation': str(self.formation1.id),
            'module': str(self.module3.id),
            'coefficient': 5
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CurriculumModule.objects.count(), 4)
        
        created = CurriculumModule.objects.get(
            formation=self.formation1,
            module=self.module3
        )
        self.assertEqual(created.coefficient, 5)
    
    def test_create_missing_formation(self):
        """Test that creating without formation fails."""
        data = {
            'module': str(self.module3.id),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('formation', response.data)
    
    def test_create_missing_module(self):
        """Test that creating without module fails."""
        data = {
            'formation': str(self.formation1.id),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('module', response.data)
    
    def test_create_missing_coefficient(self):
        """Test that creating without coefficient fails."""
        data = {
            'formation': str(self.formation1.id),
            'module': str(self.module3.id)
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('coefficient', response.data)
    
    def test_create_with_nonexistent_formation(self):
        """Test creating with nonexistent formation fails."""
        import uuid
        data = {
            'formation': str(uuid.uuid4()),
            'module': str(self.module3.id),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_with_nonexistent_module(self):
        """Test creating with nonexistent module fails."""
        import uuid
        data = {
            'formation': str(self.formation1.id),
            'module': str(uuid.uuid4()),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_duplicate_formation_module(self):
        """Test that creating duplicate formation-module combination fails."""
        data = {
            'formation': str(self.formation1.id),
            'module': str(self.module1.id),  # Already exists
            'coefficient': 5
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_same_module_different_formation(self):
        """Test creating same module in different formation succeeds."""
        data = {
            'formation': str(self.formation2.id),
            'module': str(self.module2.id),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_with_zero_coefficient(self):
        """Test creating with zero coefficient."""
        data = {
            'formation': str(self.formation2.id),
            'module': str(self.module3.id),
            'coefficient': 0
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['coefficient'], 0)
    
    # ==================== RETRIEVE TESTS ====================
    
    def test_retrieve_curriculum_module(self):
        """Test retrieving a single curriculum module by ID."""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['formation'], str(self.formation1.id))
        self.assertEqual(response.data['module'], str(self.module1.id))
        self.assertEqual(response.data['coefficient'], 3)
    
    def test_retrieve_nonexistent_curriculum_module(self):
        """Test retrieving a non-existent curriculum module returns 404."""
        import uuid
        nonexistent_url = reverse('curriculummodule-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_curriculum_module_all_fields(self):
        """Test full update of a curriculum module."""
        data = {
            'formation': str(self.formation2.id),
            'module': str(self.module2.id),
            'coefficient': 5
        }
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['formation'], str(self.formation2.id))
        self.assertEqual(response.data['module'], str(self.module2.id))
        self.assertEqual(response.data['coefficient'], 5)
    
    def test_update_to_duplicate_fails(self):
        """Test that updating to duplicate combination fails."""
        # cm2: formation1 + module2 + coef 2
        # Try to update cm2 to formation1 + module1 (which is cm1)
        detail_url = reverse('curriculummodule-detail', kwargs={'pk': self.cm2.id})
        data = {
            'formation': str(self.formation1.id),
            'module': str(self.module1.id),
            'coefficient': 5
        }
        response = self.client.put(detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_nonexistent_curriculum_module(self):
        """Test updating non-existent curriculum module returns 404."""
        import uuid
        nonexistent_url = reverse('curriculummodule-detail', kwargs={'pk': uuid.uuid4()})
        data = {
            'formation': str(self.formation1.id),
            'module': str(self.module1.id),
            'coefficient': 3
        }
        response = self.client.put(nonexistent_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ==================== PARTIAL UPDATE TESTS ====================
    
    def test_partial_update_coefficient(self):
        """Test partial update of coefficient only."""
        data = {'coefficient': 7}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['coefficient'], 7)
        self.assertEqual(response.data['module'], str(self.module1.id))  # Unchanged
    
    def test_partial_update_module(self):
        """Test partial update of module only."""
        data = {'module': str(self.module3.id)}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['module'], str(self.module3.id))
        self.assertEqual(response.data['coefficient'], 3)  # Unchanged
    
    def test_partial_update_formation(self):
        """Test partial update of formation only."""
        data = {'formation': str(self.formation2.id)}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['formation'], str(self.formation2.id))
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_curriculum_module(self):
        """Test deleting a curriculum module."""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CurriculumModule.objects.count(), 2)
    
    def test_delete_nonexistent_curriculum_module(self):
        """Test deleting non-existent curriculum module returns 404."""
        import uuid
        nonexistent_url = reverse('curriculummodule-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_keeps_formation_and_module(self):
        """Test that deleting curriculum module doesn't delete formation or module."""
        formation_id = self.formation1.id
        module_id = self.module1.id
        
        self.client.delete(self.detail_url)
        
        # Both should still exist
        self.assertTrue(Formation.objects.filter(id=formation_id).exists())
        self.assertTrue(Module.objects.filter(id=module_id).exists())
    
    # ==================== SEARCH TESTS ====================
    
    def test_search_by_formation_name(self):
        """Test searching by formation name."""
        response = self.client.get(self.list_url, {'search': 'Promotion 2024'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_search_by_module_name(self):
        """Test searching by module name."""
        response = self.client.get(self.list_url, {'search': 'Algorithmique'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_search_by_module_code(self):
        """Test searching by module code."""
        response = self.client.get(self.list_url, {'search': 'BDD201'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_search_by_coefficient(self):
        """Test searching by coefficient."""
        response = self.client.get(self.list_url, {'search': '3'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.list_url, {'search': 'NonExistent'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ==================== ORDERING TESTS ====================
    
    def test_ordering_by_coefficient_ascending(self):
        """Test ordering by coefficient ascending."""
        response = self.client.get(self.list_url, {'ordering': 'coefficient'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        coefficients = [item['coefficient'] for item in response.data]
        self.assertEqual(coefficients, sorted(coefficients))
    
    def test_ordering_by_coefficient_descending(self):
        """Test ordering by coefficient descending."""
        response = self.client.get(self.list_url, {'ordering': '-coefficient'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        coefficients = [item['coefficient'] for item in response.data]
        self.assertEqual(coefficients, sorted(coefficients, reverse=True))
    
    def test_ordering_by_created_at(self):
        """Test ordering by created_at."""
        response = self.client.get(self.list_url, {'ordering': 'created_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    # ==================== EDGE CASES ====================
    
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
            'formation': str(self.formation2.id),
            'module': str(self.module3.id),
            'coefficient': 3,
            'extra_field': 'should be ignored'
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('extra_field', response.data)
    
    def test_combined_search_and_ordering(self):
        """Test combining search and ordering."""
        response = self.client.get(
            self.list_url,
            {'search': 'Algorithmique', 'ordering': '-coefficient'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if len(response.data) > 1:
            coefficients = [item['coefficient'] for item in response.data]
            self.assertEqual(coefficients, sorted(coefficients, reverse=True))
    
    # ==================== RELATIONSHIP INTEGRITY TESTS ====================
    
    def test_list_modules_in_formation(self):
        """Test getting all modules in a formation."""
        # Get all curriculum modules for formation1
        cms = CurriculumModule.objects.filter(formation=self.formation1)
        self.assertEqual(cms.count(), 2)
        
        modules = [cm.module for cm in cms]
        self.assertIn(self.module1, modules)
        self.assertIn(self.module2, modules)
    
    def test_list_formations_using_module(self):
        """Test getting all formations using a module."""
        # module1 is in both formation1 and formation2
        cms = CurriculumModule.objects.filter(module=self.module1)
        self.assertEqual(cms.count(), 2)
        
        formations = [cm.formation for cm in cms]
        self.assertIn(self.formation1, formations)
        self.assertIn(self.formation2, formations)
    
    def test_api_verifies_formation_exists(self):
        """Test that API verifies formation exists before creating."""
        import uuid
        data = {
            'formation': str(uuid.uuid4()),
            'module': str(self.module3.id),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('formation', response.data)
    
    def test_api_verifies_module_exists(self):
        """Test that API verifies module exists before creating."""
        import uuid
        data = {
            'formation': str(self.formation1.id),
            'module': str(uuid.uuid4()),
            'coefficient': 3
        }
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('module', response.data)