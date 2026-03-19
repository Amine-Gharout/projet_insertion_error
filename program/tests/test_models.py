# program/tests/test_models.py
from django.test import TestCase
from django.db import IntegrityError
from program.models import Program
import uuid
import time


class ProgramModelTest(TestCase):
    """Tests for the Program model."""
    
    def setUp(self):
        """Set up test data that runs before each test method."""
        self.program_data = {
            'title': 'Informatique',
            'code': 'INFO101',
            'description': 'Programme en informatique',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        self.program = Program.objects.create(**self.program_data)
    
    # ==================== CREATION TESTS ====================
    
    def test_program_creation_with_all_fields(self):
        """Test creating a program with all fields."""
        self.assertEqual(self.program.title, 'Informatique')
        self.assertEqual(self.program.code, 'INFO101')
        self.assertEqual(self.program.description, 'Programme en informatique')
        self.assertEqual(self.program.cycle, 'Licence')
        self.assertEqual(self.program.diploma, 'Licence en Informatique')
        self.assertIsNotNone(self.program.id)
        self.assertIsInstance(self.program.id, uuid.UUID)
    
    def test_program_creation_without_description(self):
        """Test creating a program without description (optional field)."""
        program = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        self.assertIsNotNone(program.id)
        self.assertIsNone(program.description)
    
    def test_program_creation_with_null_description(self):
        """Test explicitly setting description to None."""
        program = Program.objects.create(
            title='Physique',
            code='PHYS301',
            description=None,
            cycle='Doctorat',
            diploma='Doctorat en Physique'
        )
        self.assertIsNone(program.description)
    
    def test_program_creation_with_blank_description(self):
        """Test that blank description is stored."""
        program = Program.objects.create(
            title='Chimie',
            code='CHEM401',
            description='',
            cycle='Licence',
            diploma='Licence en Chimie'
        )
        self.assertEqual(program.description, '')
    
    # ==================== UNIQUENESS TESTS ====================
    
    def test_title_unique_constraint(self):
        """Test that duplicate title raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Program.objects.create(
                title='Informatique',  # Duplicate
                code='DIFF001',
                cycle='Master',
                diploma='Master en Informatique'
            )
    
    def test_code_unique_constraint(self):
        """Test that duplicate code raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Program.objects.create(
                title='Different Program',
                code='INFO101',  # Duplicate
                cycle='Master',
                diploma='Master Programme'
            )
    
    def test_different_codes_and_titles_allowed(self):
        """Test that different codes and titles can coexist."""
        program = Program.objects.create(
            title='Génie Logiciel',
            code='GL101',
            cycle='Master',
            diploma='Master en Génie Logiciel'
        )
        self.assertNotEqual(self.program.code, program.code)
        self.assertNotEqual(self.program.title, program.title)
        self.assertNotEqual(self.program.id, program.id)
    
    def test_same_cycle_and_diploma_allowed(self):
        """Test that same cycle and diploma with different title/code is allowed."""
        program = Program.objects.create(
            title='Réseaux Informatiques',
            code='NET101',
            cycle='Licence',  # Same cycle
            diploma='Licence en Informatique'  # Same diploma
        )
        self.assertEqual(self.program.cycle, program.cycle)
        self.assertEqual(self.program.diploma, program.diploma)
        self.assertNotEqual(self.program.id, program.id)
    
    # ==================== UUID TESTS ====================
    
    def test_uuid_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        program = Program.objects.create(
            title='Test Program',
            code='TEST001',
            cycle='Licence',
            diploma='Test Diploma'
        )
        self.assertIsNotNone(program.id)
        self.assertIsInstance(program.id, uuid.UUID)
    
    def test_uuid_is_unique(self):
        """Test that each program gets a unique UUID."""
        program1 = Program.objects.create(
            title='Program 1',
            code='PRG001',
            cycle='Licence',
            diploma='Diploma 1'
        )
        program2 = Program.objects.create(
            title='Program 2',
            code='PRG002',
            cycle='Master',
            diploma='Diploma 2'
        )
        self.assertNotEqual(program1.id, program2.id)
    
    def test_uuid_is_not_editable(self):
        """Test that UUID field is marked as not editable."""
        field = Program._meta.get_field('id')
        self.assertFalse(field.editable)
    
    # ==================== TIMESTAMP TESTS ====================
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        self.assertIsNotNone(self.program.created_at)
    
    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set."""
        self.assertIsNotNone(self.program.updated_at)
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when program is saved."""
        original_updated_at = self.program.updated_at
        time.sleep(0.1)  # Small delay to ensure timestamp difference
        self.program.title = 'Updated Title'
        self.program.save()
        self.program.refresh_from_db()
        self.assertGreater(self.program.updated_at, original_updated_at)
    
    def test_created_at_does_not_change_on_save(self):
        """Test that created_at doesn't change on subsequent saves."""
        original_created_at = self.program.created_at
        self.program.title = 'Updated Title'
        self.program.save()
        self.program.refresh_from_db()
        self.assertEqual(self.program.created_at, original_created_at)
    
    # ==================== STRING REPRESENTATION TESTS ====================
    
    def test_str_representation(self):
        """Test the string representation of Program."""
        expected_str = 'Informatique (INFO101) - Licence - Licence en Informatique'
        self.assertEqual(str(self.program), expected_str)
    
    def test_str_with_different_values(self):
        """Test string representation with various values."""
        program = Program.objects.create(
            title='Mathématiques Appliquées',
            code='MATH501',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        expected_str = 'Mathématiques Appliquées (MATH501) - Master - Master en Mathématiques'
        self.assertEqual(str(program), expected_str)
    
    # ==================== META OPTIONS TESTS ====================
    
    def test_meta_ordering(self):
        """Test that programs are ordered by title."""
        Program.objects.create(
            title='Zebra Program',
            code='ZEB001',
            cycle='Licence',
            diploma='Zebra Diploma'
        )
        Program.objects.create(
            title='Alpha Program',
            code='ALP001',
            cycle='Licence',
            diploma='Alpha Diploma'
        )
        
        programs = Program.objects.all()
        titles = [p.title for p in programs]
        self.assertEqual(titles, sorted(titles))
    
    def test_meta_verbose_name(self):
        """Test verbose_name Meta option."""
        self.assertEqual(Program._meta.verbose_name, 'Programme')
    
    def test_meta_verbose_name_plural(self):
        """Test verbose_name_plural Meta option."""
        self.assertEqual(Program._meta.verbose_name_plural, 'Programmes')
    
    def test_meta_db_table(self):
        """Test db_table Meta option."""
        self.assertEqual(Program._meta.db_table, 'program')
    
    # ==================== FIELD CONSTRAINTS TESTS ====================
    
    def test_title_max_length(self):
        """Test title field max_length."""
        field = Program._meta.get_field('title')
        self.assertEqual(field.max_length, 100)
    
    def test_title_is_unique(self):
        """Test that title field has unique=True."""
        field = Program._meta.get_field('title')
        self.assertTrue(field.unique)
    
    def test_code_max_length(self):
        """Test code field max_length."""
        field = Program._meta.get_field('code')
        self.assertEqual(field.max_length, 20)
    
    def test_code_is_unique(self):
        """Test that code field has unique=True."""
        field = Program._meta.get_field('code')
        self.assertTrue(field.unique)
    
    def test_description_allows_null(self):
        """Test that description allows null."""
        field = Program._meta.get_field('description')
        self.assertTrue(field.null)
    
    def test_description_allows_blank(self):
        """Test that description allows blank."""
        field = Program._meta.get_field('description')
        self.assertTrue(field.blank)
    
    def test_cycle_max_length(self):
        """Test cycle field max_length."""
        field = Program._meta.get_field('cycle')
        self.assertEqual(field.max_length, 20)
    
    def test_diploma_max_length(self):
        """Test diploma field max_length."""
        field = Program._meta.get_field('diploma')
        self.assertEqual(field.max_length, 50)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_title(self):
        """Test updating program title."""
        self.program.title = 'Informatique Avancée'
        self.program.save()
        self.program.refresh_from_db()
        self.assertEqual(self.program.title, 'Informatique Avancée')
    
    def test_update_title_to_existing_value_fails(self):
        """Test that updating title to an existing value fails."""
        Program.objects.create(
            title='Other Program',
            code='OTHER001',
            cycle='Licence',
            diploma='Other Diploma'
        )
        self.program.title = 'Other Program'
        with self.assertRaises(IntegrityError):
            self.program.save()
    
    def test_update_code_to_unique_value(self):
        """Test updating code to a new unique value."""
        self.program.code = 'INFO102'
        self.program.save()
        self.program.refresh_from_db()
        self.assertEqual(self.program.code, 'INFO102')
    
    def test_update_code_to_existing_value_fails(self):
        """Test that updating code to an existing value fails."""
        Program.objects.create(
            title='Other Program',
            code='OTHER001',
            cycle='Licence',
            diploma='Other Diploma'
        )
        self.program.code = 'OTHER001'
        with self.assertRaises(IntegrityError):
            self.program.save()
    
    def test_update_description(self):
        """Test updating description."""
        new_desc = 'Nouvelle description du programme'
        self.program.description = new_desc
        self.program.save()
        self.program.refresh_from_db()
        self.assertEqual(self.program.description, new_desc)
    
    def test_update_cycle(self):
        """Test updating cycle."""
        self.program.cycle = 'Master'
        self.program.save()
        self.program.refresh_from_db()
        self.assertEqual(self.program.cycle, 'Master')
    
    def test_update_diploma(self):
        """Test updating diploma."""
        self.program.diploma = 'Master en Informatique'
        self.program.save()
        self.program.refresh_from_db()
        self.assertEqual(self.program.diploma, 'Master en Informatique')
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_program(self):
        """Test deleting a program."""
        program_id = self.program.id
        self.program.delete()
        with self.assertRaises(Program.DoesNotExist):
            Program.objects.get(id=program_id)
    
    def test_delete_allows_title_reuse(self):
        """Test that deleted program's title can be reused."""
        title = self.program.title
        self.program.delete()
        new_program = Program.objects.create(
            title=title,
            code='NEW001',
            cycle='Master',
            diploma='New Diploma'
        )
        self.assertEqual(new_program.title, title)
    
    def test_delete_allows_code_reuse(self):
        """Test that deleted program's code can be reused."""
        code = self.program.code
        self.program.delete()
        new_program = Program.objects.create(
            title='New Program',
            code=code,
            cycle='Master',
            diploma='New Diploma'
        )
        self.assertEqual(new_program.code, code)
    
    # ==================== QUERY TESTS ====================
    
    def test_filter_by_title(self):
        """Test filtering programs by title."""
        Program.objects.create(
            title='Génie Civil',
            code='GC001',
            cycle='Licence',
            diploma='Licence en Génie Civil'
        )
        programs = Program.objects.filter(title='Génie Civil')
        self.assertEqual(programs.count(), 1)
    
    def test_filter_by_code(self):
        """Test filtering programs by code."""
        programs = Program.objects.filter(code='INFO101')
        self.assertEqual(programs.count(), 1)
        self.assertEqual(programs.first().title, 'Informatique')
    
    def test_filter_by_cycle(self):
        """Test filtering programs by cycle."""
        Program.objects.create(
            title='Program 1',
            code='PRG001',
            cycle='Master',
            diploma='Master Diploma'
        )
        Program.objects.create(
            title='Program 2',
            code='PRG002',
            cycle='Master',
            diploma='Master Diploma 2'
        )
        programs = Program.objects.filter(cycle='Master')
        self.assertEqual(programs.count(), 2)
    
    def test_filter_by_diploma(self):
        """Test filtering programs by diploma."""
        programs = Program.objects.filter(diploma='Licence en Informatique')
        self.assertEqual(programs.count(), 1)
    
    def test_filter_by_title_contains(self):
        """Test filtering programs by title contains."""
        Program.objects.create(
            title='Informatique Appliquée',
            code='INFO201',
            cycle='Master',
            diploma='Master en Informatique'
        )
        programs = Program.objects.filter(title__icontains='info')
        self.assertEqual(programs.count(), 2)
    
    def test_filter_by_cycle_and_diploma(self):
        """Test filtering programs by multiple fields."""
        Program.objects.create(
            title='Program 1',
            code='PRG001',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        programs = Program.objects.filter(
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        self.assertEqual(programs.count(), 2)
