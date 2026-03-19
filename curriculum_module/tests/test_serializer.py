# curriculum_module/tests/test_serializers.py
from django.test import TestCase
from curriculum_module.models import CurriculumModule
from formation.models import Formation
from program.models import Program
from module.models import Module
from curriculum_module.serializer import CurriculumModuleSerializer
import uuid


class CurriculumModuleSerializerTest(TestCase):
    """Tests for the CurriculumModuleSerializer."""
    
    def setUp(self):
        """Set up test data."""
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
        
        # Create test modules
        self.module1 = Module.objects.create(
            name='Algorithmique',
            code='ALGO101'
        )
        self.module2 = Module.objects.create(
            name='Base de données',
            code='BDD201'
        )
        
        # Create test curriculum module
        self.curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module1,
            coefficient=3
        )
    
    # ==================== SERIALIZATION TESTS ====================
    
    def test_serialize_curriculum_module_with_all_fields(self):
        """Test serializing a curriculum module with all fields."""
        serializer = CurriculumModuleSerializer(self.curriculum_module)
        data = serializer.data
        
        self.assertEqual(data['id'], str(self.curriculum_module.id))
        self.assertEqual(data['formation'], str(self.formation.id))
        self.assertEqual(data['module'], str(self.module1.id))
        self.assertEqual(data['coefficient'], 3)
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = CurriculumModuleSerializer(self.curriculum_module)
        expected_fields = {'id', 'formation', 'module', 'coefficient'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_serializer_excludes_timestamps(self):
        """Test that created_at is not in serialized data."""
        serializer = CurriculumModuleSerializer(self.curriculum_module)
        self.assertNotIn('created_at', serializer.data)
    
    def test_serializer_returns_uuids_as_strings(self):
        """Test that foreign keys return UUIDs as strings."""
        serializer = CurriculumModuleSerializer(self.curriculum_module)
        
        # Should be string representation of UUID
        self.assertIsInstance(serializer.data['id'], str)
        self.assertIsInstance(serializer.data['formation'], str)
        self.assertIsInstance(serializer.data['module'], str)
    
    # ==================== DESERIALIZATION TESTS ====================
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid curriculum module data."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 4
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curriculum_module = serializer.save()
        
        self.assertEqual(curriculum_module.formation, self.formation)
        self.assertEqual(curriculum_module.module, self.module2)
        self.assertEqual(curriculum_module.coefficient, 4)
    
    def test_deserialize_with_uuid_objects(self):
        """Test deserializing with UUID objects instead of strings."""
        data = {
            'formation': self.formation.id,
            'module': self.module2.id,
            'coefficient': 2
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curriculum_module = serializer.save()
        self.assertEqual(curriculum_module.coefficient, 2)
    
    # ==================== VALIDATION TESTS ====================
    
    def test_invalid_without_formation(self):
        """Test that serializer is invalid without formation."""
        data = {
            'module': str(self.module1.id),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('formation', serializer.errors)
    
    def test_invalid_without_module(self):
        """Test that serializer is invalid without module."""
        data = {
            'formation': str(self.formation.id),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('module', serializer.errors)
    
    def test_invalid_without_coefficient(self):
        """Test that serializer is invalid without coefficient."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module1.id)
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('coefficient', serializer.errors)
    
    def test_invalid_with_nonexistent_formation(self):
        """Test that serializer rejects nonexistent formation."""
        data = {
            'formation': str(uuid.uuid4()),
            'module': str(self.module1.id),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('formation', serializer.errors)
    
    def test_invalid_with_nonexistent_module(self):
        """Test that serializer rejects nonexistent module."""
        data = {
            'formation': str(self.formation.id),
            'module': str(uuid.uuid4()),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('module', serializer.errors)
    
    def test_invalid_with_duplicate_formation_module(self):
        """Test that serializer rejects duplicate formation-module combination."""
        # First one already exists in setUp
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module1.id),
            'coefficient': 5
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_valid_with_same_module_different_formation(self):
        """Test that same module in different formation is valid."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        data = {
            'formation': str(formation2.id),
            'module': str(self.module1.id),
            'coefficient': 4
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_with_coefficient_as_string(self):
        """Test that coefficient accepts numeric strings (DRF converts)."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': '5'
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curriculum_module = serializer.save()
        self.assertEqual(curriculum_module.coefficient, 5)
        self.assertIsInstance(curriculum_module.coefficient, int)
    
    def test_invalid_with_coefficient_as_text(self):
        """Test that serializer rejects non-numeric coefficient."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 'not-a-number'
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('coefficient', serializer.errors)
    
    def test_valid_with_zero_coefficient(self):
        """Test that coefficient can be zero."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 0
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curriculum_module = serializer.save()
        self.assertEqual(curriculum_module.coefficient, 0)
    
    def test_valid_with_negative_coefficient(self):
        """Test that coefficient can be negative."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': -5
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curriculum_module = serializer.save()
        self.assertEqual(curriculum_module.coefficient, -5)
    
    def test_valid_with_large_coefficient(self):
        """Test that coefficient can be large."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 9999
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_coefficient(self):
        """Test updating coefficient via serializer."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module1.id),
            'coefficient': 5
        }
        serializer = CurriculumModuleSerializer(self.curriculum_module, data=data)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.coefficient, 5)
    
    def test_update_module(self):
        """Test updating module via serializer."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(self.curriculum_module, data=data)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.module, self.module2)
    
    def test_update_formation(self):
        """Test updating formation via serializer."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        data = {
            'formation': str(formation2.id),
            'module': str(self.module1.id),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(self.curriculum_module, data=data)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.formation, formation2)
    
    def test_partial_update_coefficient_only(self):
        """Test partial update with only coefficient."""
        data = {'coefficient': 7}
        serializer = CurriculumModuleSerializer(
            self.curriculum_module,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.coefficient, 7)
        self.assertEqual(updated.module, self.module1)  # Unchanged
    
    def test_partial_update_module_only(self):
        """Test partial update with only module."""
        data = {'module': str(self.module2.id)}
        serializer = CurriculumModuleSerializer(
            self.curriculum_module,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.module, self.module2)
        self.assertEqual(updated.coefficient, 3)  # Unchanged
    
    def test_partial_update_formation_only(self):
        """Test partial update with only formation."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        data = {'formation': str(formation2.id)}
        serializer = CurriculumModuleSerializer(
            self.curriculum_module,
            data=data,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.formation, formation2)
    
    def test_update_to_duplicate_fails(self):
        """Test that updating to duplicate formation-module fails."""
        # Create another curriculum module
        curriculum_module2 = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        # Try to update it to duplicate first one
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module1.id),
            'coefficient': 5
        }
        serializer = CurriculumModuleSerializer(curriculum_module2, data=data)
        self.assertFalse(serializer.is_valid())
    
    # ==================== SERIALIZATION OF MULTIPLE OBJECTS ====================
    
    def test_serialize_multiple_curriculum_modules(self):
        """Test serializing multiple curriculum modules."""
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        curriculum_modules = CurriculumModule.objects.all()
        serializer = CurriculumModuleSerializer(curriculum_modules, many=True)
        
        self.assertEqual(len(serializer.data), 2)
    
    def test_serialize_empty_queryset(self):
        """Test serializing empty queryset."""
        CurriculumModule.objects.all().delete()
        curriculum_modules = CurriculumModule.objects.all()
        serializer = CurriculumModuleSerializer(curriculum_modules, many=True)
        
        self.assertEqual(len(serializer.data), 0)
    
    # ==================== READ-ONLY FIELD TESTS ====================
    
    def test_id_is_read_only(self):
        """Test that id field is read-only."""
        new_id = uuid.uuid4()
        data = {
            'id': str(new_id),
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 4
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        curriculum_module = serializer.save()
        
        # ID should be auto-generated, not the one we provided
        self.assertNotEqual(curriculum_module.id, new_id)
    
    def test_cannot_update_id(self):
        """Test that id cannot be updated."""
        original_id = self.curriculum_module.id
        new_id = uuid.uuid4()
        
        data = {
            'id': str(new_id),
            'formation': str(self.formation.id),
            'module': str(self.module1.id),
            'coefficient': 5
        }
        serializer = CurriculumModuleSerializer(self.curriculum_module, data=data)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        
        # ID should not change
        self.assertEqual(updated.id, original_id)
        self.assertNotEqual(updated.id, new_id)
    
    # ==================== EDGE CASES ====================
    
    def test_coefficient_with_float_converts_to_int(self):
        """Test that float coefficient is converted to int."""
        data = {
            'formation': str(self.formation.id),
            'module': str(self.module2.id),
            'coefficient': 3.7
        }
        serializer = CurriculumModuleSerializer(data=data)
        if serializer.is_valid():
            curriculum_module = serializer.save()
            self.assertEqual(curriculum_module.coefficient, 3)  # Truncated
            self.assertIsInstance(curriculum_module.coefficient, int)
    
    def test_invalid_uuid_format(self):
        """Test that invalid UUID format is rejected."""
        data = {
            'formation': 'not-a-uuid',
            'module': str(self.module1.id),
            'coefficient': 3
        }
        serializer = CurriculumModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('formation', serializer.errors)