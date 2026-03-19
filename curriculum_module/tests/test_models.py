# curriculum_module/tests/test_models.py
from django.test import TestCase
from django.db import IntegrityError
from curriculum_module.models import CurriculumModule
from formation.models import Formation
from program.models import Program
from module.models import Module
import uuid


class CurriculumModuleModelTest(TestCase):
    """Tests for the CurriculumModule model."""
    
    def setUp(self):
        """Set up test data that runs before each test method."""
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
            code='ALGO101',
            description='Introduction aux algorithmes'
        )
        self.module2 = Module.objects.create(
            name='Base de données',
            code='BDD201',
            description='Gestion des bases de données'
        )
        
        # Create test curriculum module
        self.curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module1,
            coefficient=3
        )
    
    # ==================== CREATION TESTS ====================
    
    def test_curriculum_module_creation_with_all_fields(self):
        """Test creating a curriculum module with all fields."""
        self.assertEqual(self.curriculum_module.formation, self.formation)
        self.assertEqual(self.curriculum_module.module, self.module1)
        self.assertEqual(self.curriculum_module.coefficient, 3)
        self.assertIsNotNone(self.curriculum_module.id)
        self.assertIsInstance(self.curriculum_module.id, uuid.UUID)
    
    def test_curriculum_module_links_formation_and_module(self):
        """Test that curriculum module correctly links formation and module."""
        self.assertEqual(self.curriculum_module.formation.name, 'Promotion 2024')
        self.assertEqual(self.curriculum_module.module.name, 'Algorithmique')
    
    def test_create_multiple_modules_in_formation(self):
        """Test adding multiple modules to a formation."""
        curriculum_module2 = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        curriculum_modules = CurriculumModule.objects.filter(formation=self.formation)
        self.assertEqual(curriculum_modules.count(), 2)
    
    def test_same_module_different_formations(self):
        """Test that same module can be in different formations."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        curriculum_module2 = CurriculumModule.objects.create(
            formation=formation2,
            module=self.module1,  # Same module
            coefficient=4
        )
        
        self.assertEqual(self.curriculum_module.module, curriculum_module2.module)
        self.assertNotEqual(self.curriculum_module.formation, curriculum_module2.formation)
    
    def test_different_coefficients_for_same_module(self):
        """Test that same module can have different coefficients in different formations."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        curriculum_module2 = CurriculumModule.objects.create(
            formation=formation2,
            module=self.module1,
            coefficient=5
        )
        
        self.assertNotEqual(self.curriculum_module.coefficient, curriculum_module2.coefficient)
    
    # ==================== UNIQUE CONSTRAINT TESTS ====================
    
    def test_unique_together_formation_module(self):
        """Test that same module cannot be added twice to same formation."""
        with self.assertRaises(IntegrityError):
            CurriculumModule.objects.create(
                formation=self.formation,
                module=self.module1,  # Duplicate
                coefficient=5
            )
    
    def test_unique_constraint_allows_different_formations(self):
        """Test that unique constraint allows same module in different formations."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        # This should work - different formation
        curriculum_module2 = CurriculumModule.objects.create(
            formation=formation2,
            module=self.module1,
            coefficient=3
        )
        
        self.assertIsNotNone(curriculum_module2.id)
    
    def test_unique_constraint_allows_different_modules(self):
        """Test that unique constraint allows different modules in same formation."""
        # This should work - different module
        curriculum_module2 = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=3
        )
        
        self.assertIsNotNone(curriculum_module2.id)
    
    # ==================== UUID TESTS ====================
    
    def test_uuid_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=4
        )
        self.assertIsNotNone(curriculum_module.id)
        self.assertIsInstance(curriculum_module.id, uuid.UUID)
    
    def test_uuid_is_unique(self):
        """Test that each curriculum module gets a unique UUID."""
        curriculum_module2 = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        self.assertNotEqual(self.curriculum_module.id, curriculum_module2.id)
    
    def test_uuid_is_not_editable(self):
        """Test that UUID field is marked as not editable."""
        field = CurriculumModule._meta.get_field('id')
        self.assertFalse(field.editable)
    
    # ==================== TIMESTAMP TESTS ====================
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        self.assertIsNotNone(self.curriculum_module.created_at)
    
    def test_created_at_does_not_change_on_save(self):
        """Test that created_at doesn't change on subsequent saves."""
        original_created_at = self.curriculum_module.created_at
        self.curriculum_module.coefficient = 5
        self.curriculum_module.save()
        self.curriculum_module.refresh_from_db()
        self.assertEqual(self.curriculum_module.created_at, original_created_at)
    
    # ==================== STRING REPRESENTATION TESTS ====================
    
    def test_str_representation(self):
        """Test the string representation of CurriculumModule."""
        expected_str = f'Promotion 2024 - Algorithmique (Coef: 3)'
        self.assertEqual(str(self.curriculum_module), expected_str)
    
    def test_str_with_different_values(self):
        """Test string representation with various values."""
        curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=5
        )
        expected_str = f'Promotion 2024 - Base de données (Coef: 5)'
        self.assertEqual(str(curriculum_module), expected_str)
    
    # ==================== META OPTIONS TESTS ====================
    
    def test_meta_ordering(self):
        """Test that curriculum modules are ordered by formation, then module."""
        formation2 = Formation.objects.create(
            name='Alpha Formation',
            year=2023,
            program=self.program
        )
        
        CurriculumModule.objects.create(
            formation=formation2,
            module=self.module1,
            coefficient=3
        )
        
        curriculum_modules = CurriculumModule.objects.all()
        # Should be ordered by formation
        self.assertEqual(curriculum_modules.count(), 2)
    
    def test_meta_verbose_name(self):
        """Test verbose_name Meta option."""
        self.assertEqual(CurriculumModule._meta.verbose_name, 'Curriculum Module')
    
    def test_meta_verbose_name_plural(self):
        """Test verbose_name_plural Meta option."""
        self.assertEqual(CurriculumModule._meta.verbose_name_plural, 'Curriculum Modules')
    
    def test_meta_db_table(self):
        """Test db_table Meta option."""
        self.assertEqual(CurriculumModule._meta.db_table, 'curriculum_module')
    
    def test_meta_unique_together(self):
        """Test that unique_together constraint exists."""
        unique_together = CurriculumModule._meta.unique_together
        self.assertIn(('formation', 'module'), unique_together)
    
    # ==================== FIELD CONSTRAINTS TESTS ====================
    
    def test_coefficient_is_integer_field(self):
        """Test that coefficient is an IntegerField."""
        field = CurriculumModule._meta.get_field('coefficient')
        self.assertEqual(field.get_internal_type(), 'IntegerField')
    
    def test_formation_is_foreign_key(self):
        """Test that formation is a ForeignKey."""
        field = CurriculumModule._meta.get_field('formation')
        self.assertEqual(field.get_internal_type(), 'ForeignKey')
    
    def test_module_is_foreign_key(self):
        """Test that module is a ForeignKey."""
        field = CurriculumModule._meta.get_field('module')
        self.assertEqual(field.get_internal_type(), 'ForeignKey')
    
    def test_formation_related_name(self):
        """Test that formation has correct related_name."""
        field = CurriculumModule._meta.get_field('formation')
        self.assertEqual(field.remote_field.related_name, 'curriculum_modules')
    
    def test_module_related_name(self):
        """Test that module has correct related_name."""
        field = CurriculumModule._meta.get_field('module')
        self.assertEqual(field.remote_field.related_name, 'curriculum_modules')
    
    def test_formation_on_delete_cascade(self):
        """Test that formation has CASCADE on_delete."""
        field = CurriculumModule._meta.get_field('formation')
        from django.db.models import CASCADE
        self.assertEqual(field.remote_field.on_delete, CASCADE)
    
    def test_module_on_delete_cascade(self):
        """Test that module has CASCADE on_delete."""
        field = CurriculumModule._meta.get_field('module')
        from django.db.models import CASCADE
        self.assertEqual(field.remote_field.on_delete, CASCADE)
    
    # ==================== FOREIGN KEY RELATIONSHIP TESTS ====================
    
    def test_access_formation_fields(self):
        """Test accessing formation fields through curriculum module."""
        self.assertEqual(self.curriculum_module.formation.name, 'Promotion 2024')
        self.assertEqual(self.curriculum_module.formation.year, 2024)
    
    def test_access_module_fields(self):
        """Test accessing module fields through curriculum module."""
        self.assertEqual(self.curriculum_module.module.name, 'Algorithmique')
        self.assertEqual(self.curriculum_module.module.code, 'ALGO101')
    
    def test_formation_reverse_relation(self):
        """Test accessing curriculum modules from formation (reverse relation)."""
        curriculum_modules = self.formation.curriculum_modules.all()
        self.assertEqual(curriculum_modules.count(), 1)
        self.assertEqual(curriculum_modules.first(), self.curriculum_module)
    
    def test_module_reverse_relation(self):
        """Test accessing curriculum modules from module (reverse relation)."""
        curriculum_modules = self.module1.curriculum_modules.all()
        self.assertEqual(curriculum_modules.count(), 1)
        self.assertEqual(curriculum_modules.first(), self.curriculum_module)
    
    def test_multiple_curriculum_modules_per_formation(self):
        """Test that a formation can have multiple curriculum modules."""
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        curriculum_modules = self.formation.curriculum_modules.all()
        self.assertEqual(curriculum_modules.count(), 2)
    
    def test_multiple_curriculum_modules_per_module(self):
        """Test that a module can be in multiple formations."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        CurriculumModule.objects.create(
            formation=formation2,
            module=self.module1,
            coefficient=4
        )
        
        curriculum_modules = self.module1.curriculum_modules.all()
        self.assertEqual(curriculum_modules.count(), 2)
    
    # ==================== CASCADE DELETE TESTS ====================
    
    def test_cascade_delete_formation_deletes_curriculum_modules(self):
        """Test that deleting formation deletes its curriculum modules."""
        curriculum_module_id = self.curriculum_module.id
        formation_id = self.formation.id
        
        self.formation.delete()
        
        # Formation should be deleted
        self.assertFalse(Formation.objects.filter(id=formation_id).exists())
        
        # Curriculum module should also be deleted (CASCADE)
        self.assertFalse(CurriculumModule.objects.filter(id=curriculum_module_id).exists())
    
    def test_cascade_delete_module_deletes_curriculum_modules(self):
        """Test that deleting module deletes its curriculum modules."""
        curriculum_module_id = self.curriculum_module.id
        module_id = self.module1.id
        
        self.module1.delete()
        
        # Module should be deleted
        self.assertFalse(Module.objects.filter(id=module_id).exists())
        
        # Curriculum module should also be deleted (CASCADE)
        self.assertFalse(CurriculumModule.objects.filter(id=curriculum_module_id).exists())
    
    def test_deleting_curriculum_module_keeps_formation(self):
        """Test that deleting curriculum module doesn't delete the formation."""
        formation_id = self.formation.id
        self.curriculum_module.delete()
        
        # Formation should still exist
        self.assertTrue(Formation.objects.filter(id=formation_id).exists())
    
    def test_deleting_curriculum_module_keeps_module(self):
        """Test that deleting curriculum module doesn't delete the module."""
        module_id = self.module1.id
        self.curriculum_module.delete()
        
        # Module should still exist
        self.assertTrue(Module.objects.filter(id=module_id).exists())
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_coefficient(self):
        """Test updating curriculum module coefficient."""
        self.curriculum_module.coefficient = 5
        self.curriculum_module.save()
        self.curriculum_module.refresh_from_db()
        self.assertEqual(self.curriculum_module.coefficient, 5)
    
    def test_update_module(self):
        """Test changing curriculum module's module."""
        self.curriculum_module.module = self.module2
        self.curriculum_module.save()
        self.curriculum_module.refresh_from_db()
        self.assertEqual(self.curriculum_module.module, self.module2)
    
    def test_update_formation(self):
        """Test changing curriculum module's formation."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        self.curriculum_module.formation = formation2
        self.curriculum_module.save()
        self.curriculum_module.refresh_from_db()
        self.assertEqual(self.curriculum_module.formation, formation2)
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_curriculum_module(self):
        """Test deleting a curriculum module."""
        curriculum_module_id = self.curriculum_module.id
        self.curriculum_module.delete()
        with self.assertRaises(CurriculumModule.DoesNotExist):
            CurriculumModule.objects.get(id=curriculum_module_id)
    
    # ==================== QUERY TESTS ====================
    
    def test_filter_by_formation(self):
        """Test filtering curriculum modules by formation."""
        curriculum_modules = CurriculumModule.objects.filter(formation=self.formation)
        self.assertEqual(curriculum_modules.count(), 1)
    
    def test_filter_by_module(self):
        """Test filtering curriculum modules by module."""
        curriculum_modules = CurriculumModule.objects.filter(module=self.module1)
        self.assertEqual(curriculum_modules.count(), 1)
    
    def test_filter_by_coefficient(self):
        """Test filtering curriculum modules by coefficient."""
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=3
        )
        
        curriculum_modules = CurriculumModule.objects.filter(coefficient=3)
        self.assertEqual(curriculum_modules.count(), 2)
    
    def test_filter_by_formation_name(self):
        """Test filtering curriculum modules by related formation name."""
        curriculum_modules = CurriculumModule.objects.filter(formation__name='Promotion 2024')
        self.assertEqual(curriculum_modules.count(), 1)
    
    def test_filter_by_module_code(self):
        """Test filtering curriculum modules by related module code."""
        curriculum_modules = CurriculumModule.objects.filter(module__code='ALGO101')
        self.assertEqual(curriculum_modules.count(), 1)
    
    def test_filter_by_formation_year(self):
        """Test filtering curriculum modules by formation year."""
        curriculum_modules = CurriculumModule.objects.filter(formation__year=2024)
        self.assertEqual(curriculum_modules.count(), 1)
    
    # ==================== VALIDATION TESTS ====================
    
    def test_coefficient_can_be_zero(self):
        """Test that coefficient can be zero."""
        curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=0
        )
        self.assertEqual(curriculum_module.coefficient, 0)
    
    def test_coefficient_can_be_negative(self):
        """Test that coefficient can be negative (edge case)."""
        curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=-5
        )
        self.assertEqual(curriculum_module.coefficient, -5)
    
    def test_coefficient_can_be_large_number(self):
        """Test that coefficient can be a large number."""
        curriculum_module = CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=9999
        )
        self.assertEqual(curriculum_module.coefficient, 9999)
    
    # ==================== COMPLEX QUERY TESTS ====================
    
    def test_get_all_modules_in_formation(self):
        """Test getting all modules in a formation via curriculum modules."""
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        curriculum_modules = self.formation.curriculum_modules.all()
        modules = [cm.module for cm in curriculum_modules]
        
        self.assertEqual(len(modules), 2)
        self.assertIn(self.module1, modules)
        self.assertIn(self.module2, modules)
    
    def test_get_all_formations_using_module(self):
        """Test getting all formations using a module via curriculum modules."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        
        CurriculumModule.objects.create(
            formation=formation2,
            module=self.module1,
            coefficient=4
        )
        
        curriculum_modules = self.module1.curriculum_modules.all()
        formations = [cm.formation for cm in curriculum_modules]
        
        self.assertEqual(len(formations), 2)
        self.assertIn(self.formation, formations)
        self.assertIn(formation2, formations)
    
    def test_get_total_coefficients_for_formation(self):
        """Test calculating total coefficients for a formation."""
        CurriculumModule.objects.create(
            formation=self.formation,
            module=self.module2,
            coefficient=2
        )
        
        from django.db.models import Sum
        total = self.formation.curriculum_modules.aggregate(
            total=Sum('coefficient')
        )['total']
        
        self.assertEqual(total, 5)  # 3 + 2