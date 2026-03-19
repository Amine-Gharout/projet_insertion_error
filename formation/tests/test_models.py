# formation/tests/test_models.py
from django.test import TestCase
from django.db import IntegrityError
from formation.models import Formation
from program.models import Program
import uuid
import time


class FormationModelTest(TestCase):
    """Tests for the Formation model."""
    
    def setUp(self):
        """Set up test data that runs before each test method."""
        # Create test program
        self.program = Program.objects.create(
            title='Informatique',
            code='INFO101',
            cycle='Licence',
            diploma='Licence en Informatique'
        )
        
        self.formation_data = {
            'name': 'Promotion 2024',
            'year': 2024,
            'program': self.program
        }
        self.formation = Formation.objects.create(**self.formation_data)
    
    # ==================== CREATION TESTS ====================
    
    def test_formation_creation_with_all_fields(self):
        """Test creating a formation with all fields."""
        self.assertEqual(self.formation.name, 'Promotion 2024')
        self.assertEqual(self.formation.year, 2024)
        self.assertEqual(self.formation.program, self.program)
        self.assertIsNotNone(self.formation.id)
        self.assertIsInstance(self.formation.id, uuid.UUID)
    
    def test_formation_creation_links_to_program(self):
        """Test that formation is correctly linked to program."""
        self.assertEqual(self.formation.program.title, 'Informatique')
        self.assertEqual(self.formation.program.code, 'INFO101')
    
    def test_formation_with_different_year(self):
        """Test creating formations with different years."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        self.assertEqual(formation2.year, 2025)
        self.assertNotEqual(self.formation.year, formation2.year)
    
    def test_multiple_formations_same_program(self):
        """Test multiple formations can belong to same program."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        self.assertEqual(self.formation.program, formation2.program)
        self.assertNotEqual(self.formation.id, formation2.id)
    
    def test_formation_with_same_name_different_program(self):
        """Test formations with same name can exist for different programs."""
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        formation2 = Formation.objects.create(
            name='Promotion 2024',  # Same name
            year=2024,
            program=program2
        )
        self.assertEqual(self.formation.name, formation2.name)
        self.assertNotEqual(self.formation.program, formation2.program)
    
    # ==================== UUID TESTS ====================
    
    def test_uuid_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        formation = Formation.objects.create(
            name='Test Formation',
            year=2023,
            program=self.program
        )
        self.assertIsNotNone(formation.id)
        self.assertIsInstance(formation.id, uuid.UUID)
    
    def test_uuid_is_unique(self):
        """Test that each formation gets a unique UUID."""
        formation1 = Formation.objects.create(
            name='Formation 1',
            year=2023,
            program=self.program
        )
        formation2 = Formation.objects.create(
            name='Formation 2',
            year=2024,
            program=self.program
        )
        self.assertNotEqual(formation1.id, formation2.id)
    
    def test_uuid_is_not_editable(self):
        """Test that UUID field is marked as not editable."""
        field = Formation._meta.get_field('id')
        self.assertFalse(field.editable)
    
    # ==================== TIMESTAMP TESTS ====================
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        self.assertIsNotNone(self.formation.created_at)
    
    def test_created_at_does_not_change_on_save(self):
        """Test that created_at doesn't change on subsequent saves."""
        original_created_at = self.formation.created_at
        self.formation.name = 'Updated Name'
        self.formation.save()
        self.formation.refresh_from_db()
        self.assertEqual(self.formation.created_at, original_created_at)
    
    # ==================== STRING REPRESENTATION TESTS ====================
    
    def test_str_representation(self):
        """Test the string representation of Formation."""
        expected_str = 'Promotion 2024 2024 '
        self.assertEqual(str(self.formation), expected_str)
    
    def test_str_with_different_values(self):
        """Test string representation with various values."""
        formation = Formation.objects.create(
            name='Promo A',
            year=2023,
            program=self.program
        )
        expected_str = 'Promo A 2023 '
        self.assertEqual(str(formation), expected_str)
    
    # ==================== META OPTIONS TESTS ====================
    
    def test_meta_ordering(self):
        """Test that formations are ordered by year."""
        Formation.objects.create(name='Promo 2026', year=2026, program=self.program)
        Formation.objects.create(name='Promo 2023', year=2023, program=self.program)
        
        formations = Formation.objects.all()
        years = [f.year for f in formations]
        self.assertEqual(years, sorted(years))
    
    def test_meta_verbose_name(self):
        """Test verbose_name Meta option."""
        self.assertEqual(Formation._meta.verbose_name, 'formation')
    
    def test_meta_verbose_name_plural(self):
        """Test verbose_name_plural Meta option."""
        self.assertEqual(Formation._meta.verbose_name_plural, 'formations')
    
    def test_meta_db_table(self):
        """Test db_table Meta option."""
        self.assertEqual(Formation._meta.db_table, 'formation')
    
    # ==================== FIELD CONSTRAINTS TESTS ====================
    
    def test_name_max_length(self):
        """Test name field max_length."""
        field = Formation._meta.get_field('name')
        self.assertEqual(field.max_length, 120)
    
    def test_year_is_integer_field(self):
        """Test that year is an IntegerField."""
        field = Formation._meta.get_field('year')
        self.assertEqual(field.get_internal_type(), 'IntegerField')
    
    def test_program_is_foreign_key(self):
        """Test that program is a ForeignKey."""
        field = Formation._meta.get_field('program')
        self.assertEqual(field.get_internal_type(), 'ForeignKey')
    
    def test_program_related_name(self):
        """Test that program has correct related_name."""
        field = Formation._meta.get_field('program')
        self.assertEqual(field.remote_field.related_name, 'formation')
    
    def test_program_on_delete_cascade(self):
        """Test that program has CASCADE on_delete."""
        field = Formation._meta.get_field('program')
        from django.db.models import CASCADE
        self.assertEqual(field.remote_field.on_delete, CASCADE)
    
    # ==================== FOREIGN KEY RELATIONSHIP TESTS ====================
    
    def test_formation_access_program_fields(self):
        """Test accessing program fields through formation."""
        self.assertEqual(self.formation.program.title, 'Informatique')
        self.assertEqual(self.formation.program.code, 'INFO101')
        self.assertEqual(self.formation.program.cycle, 'Licence')
    
    def test_program_access_formations_reverse_relation(self):
        """Test accessing formations from program (reverse relation)."""
        formations = self.program.formation.all()
        self.assertEqual(formations.count(), 1)
        self.assertEqual(formations.first(), self.formation)
    
    def test_multiple_formations_per_program(self):
        """Test that a program can have multiple formations."""
        formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
            program=self.program
        )
        formation3 = Formation.objects.create(
            name='Promotion 2026',
            year=2026,
            program=self.program
        )
        
        formations = self.program.formation.all()
        self.assertEqual(formations.count(), 3)
    
    def test_cascade_delete_program_deletes_formations(self):
        """Test that deleting program deletes associated formations."""
        formation_id = self.formation.id
        program_id = self.program.id
        
        self.program.delete()
        
        # Program should be deleted
        self.assertFalse(Program.objects.filter(id=program_id).exists())
        
        # Formation should also be deleted (CASCADE)
        self.assertFalse(Formation.objects.filter(id=formation_id).exists())
    
    def test_deleting_formation_does_not_delete_program(self):
        """Test that deleting formation doesn't delete the program."""
        program_id = self.program.id
        self.formation.delete()
        
        # Program should still exist
        self.assertTrue(Program.objects.filter(id=program_id).exists())
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_name(self):
        """Test updating formation name."""
        self.formation.name = 'Nouvelle Promotion'
        self.formation.save()
        self.formation.refresh_from_db()
        self.assertEqual(self.formation.name, 'Nouvelle Promotion')
    
    def test_update_year(self):
        """Test updating formation year."""
        self.formation.year = 2025
        self.formation.save()
        self.formation.refresh_from_db()
        self.assertEqual(self.formation.year, 2025)
    
    def test_update_program(self):
        """Test changing formation's program."""
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        self.formation.program = program2
        self.formation.save()
        self.formation.refresh_from_db()
        self.assertEqual(self.formation.program, program2)
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_formation(self):
        """Test deleting a formation."""
        formation_id = self.formation.id
        self.formation.delete()
        with self.assertRaises(Formation.DoesNotExist):
            Formation.objects.get(id=formation_id)
    
    # ==================== QUERY TESTS ====================
    
    def test_filter_by_name(self):
        """Test filtering formations by name."""
        Formation.objects.create(name='Promo A', year=2023, program=self.program)
        formations = Formation.objects.filter(name='Promo A')
        self.assertEqual(formations.count(), 1)
    
    def test_filter_by_year(self):
        """Test filtering formations by year."""
        Formation.objects.create(name='Promo 2023', year=2023, program=self.program)
        Formation.objects.create(name='Promo 2024-2', year=2024, program=self.program)
        
        formations = Formation.objects.filter(year=2024)
        self.assertEqual(formations.count(), 2)
    
    def test_filter_by_program(self):
        """Test filtering formations by program."""
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        Formation.objects.create(name='Math Promo', year=2024, program=program2)
        
        formations = Formation.objects.filter(program=self.program)
        self.assertEqual(formations.count(), 1)
        self.assertEqual(formations.first().program.title, 'Informatique')
    
    def test_filter_by_name_contains(self):
        """Test filtering formations by name contains."""
        Formation.objects.create(name='Promotion Spéciale', year=2023, program=self.program)
        formations = Formation.objects.filter(name__icontains='promo')
        self.assertEqual(formations.count(), 2)
    
    def test_filter_by_year_range(self):
        """Test filtering formations by year range."""
        Formation.objects.create(name='Promo 2023', year=2023, program=self.program)
        Formation.objects.create(name='Promo 2025', year=2025, program=self.program)
        Formation.objects.create(name='Promo 2026', year=2026, program=self.program)
        
        formations = Formation.objects.filter(year__gte=2024, year__lte=2025)
        self.assertEqual(formations.count(), 2)
    
    def test_filter_by_program_title(self):
        """Test filtering formations by related program title."""
        formations = Formation.objects.filter(program__title='Informatique')
        self.assertEqual(formations.count(), 1)
    
    def test_filter_by_program_cycle(self):
        """Test filtering formations by program cycle."""
        formations = Formation.objects.filter(program__cycle='Licence')
        self.assertEqual(formations.count(), 1)
    
    # ==================== VALIDATION TESTS ====================
    
    def test_year_can_be_negative(self):
        """Test that year can be negative (historical data)."""
        formation = Formation.objects.create(
            name='Historical Formation',
            year=-500,
            program=self.program
        )
        self.assertEqual(formation.year, -500)
    
    def test_year_can_be_zero(self):
        """Test that year can be zero."""
        formation = Formation.objects.create(
            name='Year Zero',
            year=0,
            program=self.program
        )
        self.assertEqual(formation.year, 0)
    
    def test_year_can_be_large_number(self):
        """Test that year can be a large number."""
        formation = Formation.objects.create(
            name='Future Formation',
            year=9999,
            program=self.program
        )
        self.assertEqual(formation.year, 9999)
    
    # ==================== EDGE CASES ====================
    
    def test_formation_with_special_characters_in_name(self):
        """Test formation with special characters in name."""
        formation = Formation.objects.create(
            name='Promotion 2024 - Spéciale & Avancée',
            year=2024,
            program=self.program
        )
        self.assertEqual(formation.name, 'Promotion 2024 - Spéciale & Avancée')
    
    def test_formation_with_unicode_in_name(self):
        """Test formation with unicode characters in name."""
        formation = Formation.objects.create(
            name='Promotion العربية 中文',
            year=2024,
            program=self.program
        )
        self.assertEqual(formation.name, 'Promotion العربية 中文')
    
    def test_formation_with_long_name(self):
        """Test formation with name at max length."""
        long_name = 'A' * 120
        formation = Formation.objects.create(
            name=long_name,
            year=2024,
            program=self.program
        )
        self.assertEqual(len(formation.name), 120)
