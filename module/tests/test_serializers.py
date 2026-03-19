# module/tests/test_serializers.py
from django.test import TestCase
from module.models import Module
from module.serializer import ModuleSerializer


class ModuleSerializerTest(TestCase):
    """Tests for the ModuleSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.module_data = {
            'name': 'Algorithmique',
            'code': 'ALGO101',
            'description': 'Introduction aux algorithmes'
        }
        self.module = Module.objects.create(**self.module_data)
    
    # ==================== SERIALIZATION TESTS ====================
    
    def test_serialize_module_with_all_fields(self):
        """Test serializing a module with all fields."""
        serializer = ModuleSerializer(self.module)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Algorithmique')
        self.assertEqual(data['code'], 'ALGO101')
        self.assertEqual(data['description'], 'Introduction aux algorithmes')
    
    def test_serialize_module_without_description(self):
        """Test serializing a module without description."""
        module = Module.objects.create(
            name='Base de données',
            code='BDD201',
            description=None
        )
        serializer = ModuleSerializer(module)
        self.assertIsNone(serializer.data['description'])
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = ModuleSerializer(self.module)
        expected_fields = {'name', 'code', 'description'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_serializer_excludes_id_and_timestamps(self):
        """Test that id and timestamps are not in serialized data."""
        serializer = ModuleSerializer(self.module)
        self.assertNotIn('id', serializer.data)
        self.assertNotIn('created_at', serializer.data)
        self.assertNotIn('updated_at', serializer.data)
    
    # ==================== DESERIALIZATION TESTS ====================
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid module data."""
        data = {
            'name': 'Programmation',
            'code': 'PROG101',
            'description': 'Introduction à la programmation'
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        
        self.assertEqual(module.name, 'Programmation')
        self.assertEqual(module.code, 'PROG101')
        self.assertEqual(module.description, 'Introduction à la programmation')
    
    def test_deserialize_without_description(self):
        """Test deserializing data without description."""
        data = {
            'name': 'Réseaux',
            'code': 'NET201'
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        self.assertIsNone(module.description)
    
    def test_deserialize_with_null_description(self):
        """Test deserializing with explicit null description."""
        data = {
            'name': 'Systèmes',
            'code': 'SYS301',
            'description': None
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        self.assertIsNone(module.description)
    
    def test_deserialize_with_empty_description(self):
        """Test deserializing with empty string description."""
        data = {
            'name': 'Sécurité',
            'code': 'SEC401',
            'description': ''
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        self.assertEqual(module.description, '')
    
    # ==================== VALIDATION TESTS ====================
    
    def test_invalid_without_name(self):
        """Test that serializer is invalid without name."""
        data = {
            'code': 'TEST001',
            'description': 'Test description'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_invalid_without_code(self):
        """Test that serializer is invalid without code."""
        data = {
            'name': 'Test Module',
            'description': 'Test description'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_invalid_with_duplicate_code(self):
        """Test that serializer rejects duplicate code."""
        data = {
            'name': 'Another Module',
            'code': 'ALGO101',  # Already exists
            'description': 'Test'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_invalid_with_empty_name(self):
        """Test that serializer rejects empty name."""
        data = {
            'name': '',
            'code': 'TEST001',
            'description': 'Test'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_invalid_with_empty_code(self):
        """Test that serializer rejects empty code."""
        data = {
            'name': 'Test Module',
            'code': '',
            'description': 'Test'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_invalid_with_code_too_long(self):
        """Test that serializer rejects code longer than 20 characters."""
        data = {
            'name': 'Test Module',
            'code': 'A' * 21,  # 21 characters
            'description': 'Test'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_valid_with_code_at_max_length(self):
        """Test that serializer accepts code at max length (20 chars)."""
        data = {
            'name': 'Test Module',
            'code': 'A' * 20,  # Exactly 20 characters
            'description': 'Test'
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_name_max_length_exceeded(self):
        """Test that serializer rejects name longer than 255 characters."""
        data = {
            'name': 'A' * 256,  # 256 characters
            'code': 'TEST001',
            'description': 'Test'
        }
        serializer = ModuleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_module_name(self):
        """Test updating module name via serializer."""
        data = {'name': 'Algorithmique Avancée', 'code': 'ALGO101', 'description': 'Updated'}
        serializer = ModuleSerializer(self.module, data=data)
        self.assertTrue(serializer.is_valid())
        updated_module = serializer.save()
        self.assertEqual(updated_module.name, 'Algorithmique Avancée')
    
    def test_update_module_code(self):
        """Test updating module code via serializer."""
        data = {'name': 'Algorithmique', 'code': 'ALGO102', 'description': 'Test'}
        serializer = ModuleSerializer(self.module, data=data)
        self.assertTrue(serializer.is_valid())
        updated_module = serializer.save()
        self.assertEqual(updated_module.code, 'ALGO102')
    
    def test_update_module_description(self):
        """Test updating module description via serializer."""
        data = {'name': 'Algorithmique', 'code': 'ALGO101', 'description': 'Nouvelle description'}
        serializer = ModuleSerializer(self.module, data=data)
        self.assertTrue(serializer.is_valid())
        updated_module = serializer.save()
        self.assertEqual(updated_module.description, 'Nouvelle description')
    
    def test_partial_update_name_only(self):
        """Test partial update with only name."""
        data = {'name': 'Nouveau Nom'}
        serializer = ModuleSerializer(self.module, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_module = serializer.save()
        self.assertEqual(updated_module.name, 'Nouveau Nom')
        self.assertEqual(updated_module.code, 'ALGO101')  # Unchanged
    
    def test_partial_update_code_only(self):
        """Test partial update with only code."""
        data = {'code': 'NEW001'}
        serializer = ModuleSerializer(self.module, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_module = serializer.save()
        self.assertEqual(updated_module.code, 'NEW001')
        self.assertEqual(updated_module.name, 'Algorithmique')  # Unchanged
    
    def test_partial_update_description_only(self):
        """Test partial update with only description."""
        data = {'description': 'Nouvelle description'}
        serializer = ModuleSerializer(self.module, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_module = serializer.save()
        self.assertEqual(updated_module.description, 'Nouvelle description')
    
    # ==================== SERIALIZATION OF MULTIPLE OBJECTS ====================
    
    def test_serialize_multiple_modules(self):
        """Test serializing multiple modules."""
        Module.objects.create(name='Module 2', code='MOD002')
        Module.objects.create(name='Module 3', code='MOD003')
        
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        
        self.assertEqual(len(serializer.data), 3)
    
    def test_serialize_empty_queryset(self):
        """Test serializing empty queryset."""
        Module.objects.all().delete()
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        
        self.assertEqual(len(serializer.data), 0)
    
    # ==================== EDGE CASES ====================
    
    def test_special_characters_in_name(self):
        """Test module with special characters in name."""
        data = {
            'name': 'Programmation C++ & C#',
            'code': 'CPP001',
            'description': 'Description <test>'
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        self.assertEqual(module.name, 'Programmation C++ & C#')
    
    def test_unicode_characters(self):
        """Test module with unicode characters."""
        data = {
            'name': 'Mathématiques العربية',
            'code': 'MATH001',
            'description': 'Description avec accents éèê'
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        self.assertEqual(module.name, 'Mathématiques العربية')
    
    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is trimmed by DRF."""
        data = {
            'name': '  Module with spaces  ',
            'code': 'SPACE001',
            'description': 'Description  with   spaces'
        }
        serializer = ModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        module = serializer.save()
        # DRF CharFields trim whitespace by default
        self.assertEqual(module.name, 'Module with spaces')
