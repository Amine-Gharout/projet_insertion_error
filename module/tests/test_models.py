# module/tests/test_models.py
from django.test import TestCase
from django.db import IntegrityError
from module.models import Module
import uuid
import time


class ModuleModelTest(TestCase):
    """Tests for the Module model."""
    
    def setUp(self):
        """Set up test data that runs before each test method."""
        self.module_data = {
            'name': 'Algorithmique',
            'code': 'ALGO101',
            'description': 'Introduction aux algorithmes'
        }
        self.module = Module.objects.create(**self.module_data)
    
    # ==================== CREATION TESTS ====================
    
    def test_module_creation_with_all_fields(self):
        """Test creating a module with all fields."""
        self.assertEqual(self.module.name, 'Algorithmique')
        self.assertEqual(self.module.code, 'ALGO101')
        self.assertEqual(self.module.description, 'Introduction aux algorithmes')
        self.assertIsNotNone(self.module.id)
        self.assertIsInstance(self.module.id, uuid.UUID)
    
    def test_module_creation_without_description(self):
        """Test creating a module without description (optional field)."""
        module = Module.objects.create(
            name='Base de données',
            code='BDD201'
        )
        self.assertIsNotNone(module.id)
        self.assertIsNone(module.description)
    
    def test_module_creation_with_null_description(self):
        """Test explicitly setting description to None."""
        module = Module.objects.create(
            name='Systèmes d\'exploitation',
            code='SYS301',
            description=None
        )
        self.assertIsNone(module.description)
    
    def test_module_creation_with_blank_description(self):
        """Test that blank description is stored."""
        module = Module.objects.create(
            name='Réseaux',
            code='NET401',
            description=''
        )
        self.assertEqual(module.description, '')
    
    # ==================== UNIQUENESS TESTS ====================
    
    def test_code_unique_constraint(self):
        """Test that duplicate code raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Module.objects.create(
                name='Different Module',
                code='ALGO101',  # Duplicate
                description='Another module with same code'
            )
    
    def test_different_codes_allowed(self):
        """Test that different codes can coexist."""
        module = Module.objects.create(
            name='Programmation',
            code='PROG101',
            description='Introduction à la programmation'
        )
        self.assertNotEqual(self.module.code, module.code)
        self.assertNotEqual(self.module.id, module.id)
    
    def test_same_name_different_code_allowed(self):
        """Test that same name with different code is allowed."""
        module = Module.objects.create(
            name='Algorithmique',  # Same name
            code='ALGO201',  # Different code
            description='Algorithmique avancée'
        )
        self.assertEqual(self.module.name, module.name)
        self.assertNotEqual(self.module.code, module.code)
    
    # ==================== UUID TESTS ====================
    
    def test_uuid_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        module = Module.objects.create(
            name='Test Module',
            code='TEST001'
        )
        self.assertIsNotNone(module.id)
        self.assertIsInstance(module.id, uuid.UUID)
    
    def test_uuid_is_unique(self):
        """Test that each module gets a unique UUID."""
        module1 = Module.objects.create(name='Module 1', code='MOD001')
        module2 = Module.objects.create(name='Module 2', code='MOD002')
        self.assertNotEqual(module1.id, module2.id)
    
    def test_uuid_is_not_editable(self):
        """Test that UUID field is marked as not editable."""
        field = Module._meta.get_field('id')
        self.assertFalse(field.editable)
    
    # ==================== TIMESTAMP TESTS ====================
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        self.assertIsNotNone(self.module.created_at)
    
    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set."""
        self.assertIsNotNone(self.module.updated_at)
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when module is saved."""
        original_updated_at = self.module.updated_at
        time.sleep(0.1)  # Small delay to ensure timestamp difference
        self.module.name = 'Updated Name'
        self.module.save()
        self.module.refresh_from_db()
        self.assertGreater(self.module.updated_at, original_updated_at)
    
    def test_created_at_does_not_change_on_save(self):
        """Test that created_at doesn't change on subsequent saves."""
        original_created_at = self.module.created_at
        self.module.name = 'Updated Name'
        self.module.save()
        self.module.refresh_from_db()
        self.assertEqual(self.module.created_at, original_created_at)
    
    # ==================== STRING REPRESENTATION TESTS ====================
    
    def test_str_representation(self):
        """Test the string representation of Module."""
        expected_str = 'Algorithmique (ALGO101)'
        self.assertEqual(str(self.module), expected_str)
    
    def test_str_with_different_values(self):
        """Test string representation with various values."""
        module = Module.objects.create(
            name='Base de données',
            code='BDD201'
        )
        expected_str = 'Base de données (BDD201)'
        self.assertEqual(str(module), expected_str)
    
    # ==================== META OPTIONS TESTS ====================
    
    def test_meta_ordering(self):
        """Test that modules are ordered by name."""
        Module.objects.create(name='Zebra Module', code='ZEB001')
        Module.objects.create(name='Alpha Module', code='ALP001')
        
        modules = Module.objects.all()
        names = [m.name for m in modules]
        self.assertEqual(names, sorted(names))
    
    def test_meta_verbose_name(self):
        """Test verbose_name Meta option."""
        self.assertEqual(Module._meta.verbose_name, 'Module')
    
    def test_meta_verbose_name_plural(self):
        """Test verbose_name_plural Meta option."""
        self.assertEqual(Module._meta.verbose_name_plural, 'Modules')
    
    def test_meta_db_table(self):
        """Test db_table Meta option."""
        self.assertEqual(Module._meta.db_table, 'module')
    
    # ==================== FIELD CONSTRAINTS TESTS ====================
    
    def test_name_max_length(self):
        """Test name field max_length."""
        field = Module._meta.get_field('name')
        self.assertEqual(field.max_length, 255)
    
    def test_code_max_length(self):
        """Test code field max_length."""
        field = Module._meta.get_field('code')
        self.assertEqual(field.max_length, 20)
    
    def test_code_is_unique(self):
        """Test that code field has unique=True."""
        field = Module._meta.get_field('code')
        self.assertTrue(field.unique)
    
    def test_description_allows_null(self):
        """Test that description allows null."""
        field = Module._meta.get_field('description')
        self.assertTrue(field.null)
    
    def test_description_allows_blank(self):
        """Test that description allows blank."""
        field = Module._meta.get_field('description')
        self.assertTrue(field.blank)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_name(self):
        """Test updating module name."""
        self.module.name = 'Algorithmique Avancée'
        self.module.save()
        self.module.refresh_from_db()
        self.assertEqual(self.module.name, 'Algorithmique Avancée')
    
    def test_update_code_to_unique_value(self):
        """Test updating code to a new unique value."""
        self.module.code = 'ALGO102'
        self.module.save()
        self.module.refresh_from_db()
        self.assertEqual(self.module.code, 'ALGO102')
    
    def test_update_code_to_existing_value_fails(self):
        """Test that updating code to an existing value fails."""
        Module.objects.create(name='Other Module', code='OTHER001')
        self.module.code = 'OTHER001'
        with self.assertRaises(IntegrityError):
            self.module.save()
    
    def test_update_description(self):
        """Test updating description."""
        new_desc = 'Mise à jour de la description'
        self.module.description = new_desc
        self.module.save()
        self.module.refresh_from_db()
        self.assertEqual(self.module.description, new_desc)
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_module(self):
        """Test deleting a module."""
        module_id = self.module.id
        self.module.delete()
        with self.assertRaises(Module.DoesNotExist):
            Module.objects.get(id=module_id)
    
    def test_delete_allows_code_reuse(self):
        """Test that deleted module's code can be reused."""
        code = self.module.code
        self.module.delete()
        new_module = Module.objects.create(name='New Module', code=code)
        self.assertEqual(new_module.code, code)
    
    # ==================== QUERY TESTS ====================
    
    def test_filter_by_name(self):
        """Test filtering modules by name."""
        Module.objects.create(name='Programming', code='PROG001')
        modules = Module.objects.filter(name='Programming')
        self.assertEqual(modules.count(), 1)
    
    def test_filter_by_code(self):
        """Test filtering modules by code."""
        modules = Module.objects.filter(code='ALGO101')
        self.assertEqual(modules.count(), 1)
        self.assertEqual(modules.first().name, 'Algorithmique')
    
    def test_filter_by_name_contains(self):
        """Test filtering modules by name contains."""
        Module.objects.create(name='Algorithme Avancé', code='ALGO201')
        modules = Module.objects.filter(name__icontains='algo')
        self.assertEqual(modules.count(), 2)
