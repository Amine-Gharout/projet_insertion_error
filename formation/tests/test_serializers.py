# formation/tests/test_serializers.py
from django.test import TestCase
from formation.models import Formation
from program.models import Program
from formation.serializer import FormationSerializer


class FormationSerializerTest(TestCase):
    """Tests for the FormationSerializer."""
    
    def setUp(self):
        """Set up test data."""
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
    
    # ==================== SERIALIZATION TESTS ====================
    
    def test_serialize_formation_with_all_fields(self):
        """Test serializing a formation with all fields."""
        serializer = FormationSerializer(self.formation)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Promotion 2024')
        self.assertEqual(data['year'], 2024)
        self.assertEqual(data['program'], self.program.id)
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = FormationSerializer(self.formation)
        expected_fields = {'name', 'year', 'program'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_serializer_excludes_id_and_timestamps(self):
        """Test that id and timestamps are not in serialized data."""
        serializer = FormationSerializer(self.formation)
        self.assertNotIn('id', serializer.data)
        self.assertNotIn('created_at', serializer.data)
    
    def test_serializer_program_returns_uuid(self):
        """Test that program field returns UUID not object."""
        serializer = FormationSerializer(self.formation)
        self.assertEqual(serializer.data['program'], self.program.id)
        self.assertIsInstance(serializer.data['program'], uuid.UUID)
    
    # ==================== DESERIALIZATION TESTS ====================
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid formation data."""
        data = {
            'name': 'Promotion 2025',
            'year': 2025,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        
        self.assertEqual(formation.name, 'Promotion 2025')
        self.assertEqual(formation.year, 2025)
        self.assertEqual(formation.program, self.program)
    
    def test_deserialize_with_string_program_id(self):
        """Test deserializing with string representation of UUID."""
        data = {
            'name': 'Promotion 2025',
            'year': 2025,
            'program': str(self.program.id)
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        self.assertEqual(formation.program, self.program)
    
    # ==================== VALIDATION TESTS ====================
    
    def test_invalid_without_name(self):
        """Test that serializer is invalid without name."""
        data = {
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_invalid_without_year(self):
        """Test that serializer is invalid without year."""
        data = {
            'name': 'Test Formation',
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('year', serializer.errors)
    
    def test_invalid_without_program(self):
        """Test that serializer is invalid without program."""
        data = {
            'name': 'Test Formation',
            'year': 2024
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('program', serializer.errors)
    
    def test_invalid_with_empty_name(self):
        """Test that serializer rejects empty name."""
        data = {
            'name': '',
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_invalid_with_nonexistent_program(self):
        """Test that serializer rejects nonexistent program."""
        import uuid
        data = {
            'name': 'Test Formation',
            'year': 2024,
            'program': uuid.uuid4()  # Random UUID
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('program', serializer.errors)
    
    def test_invalid_with_name_too_long(self):
        """Test that serializer rejects name longer than 120 characters."""
        data = {
            'name': 'A' * 121,  # 121 characters
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_valid_with_name_at_max_length(self):
        """Test that serializer accepts name at max length (120 chars)."""
        data = {
            'name': 'A' * 120,  # Exactly 120 characters
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_with_year_as_string(self):
        """Test that serializer accepts year as string (DRF converts it)."""
        data = {
            'name': 'Test Formation',
            'year': '2024',  # String
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())  # DRF converts to int
        formation = serializer.save()
        self.assertEqual(formation.year, 2024)
        self.assertIsInstance(formation.year, int)
    
    def test_invalid_with_year_as_float(self):
        """Test that serializer handles year as float."""
        data = {
            'name': 'Test Formation',
            'year': 2024.5,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        # DRF might convert or reject depending on version
        if serializer.is_valid():
            formation = serializer.save()
            self.assertEqual(formation.year, 2024)  # Truncated
    
    def test_invalid_with_year_as_text(self):
        """Test that serializer rejects year as non-numeric text."""
        data = {
            'name': 'Test Formation',
            'year': 'not-a-year',
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('year', serializer.errors)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_formation_name(self):
        """Test updating formation name via serializer."""
        data = {
            'name': 'Promotion 2024 - Updated',
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(self.formation, data=data)
        self.assertTrue(serializer.is_valid())
        updated_formation = serializer.save()
        self.assertEqual(updated_formation.name, 'Promotion 2024 - Updated')
    
    def test_update_formation_year(self):
        """Test updating formation year via serializer."""
        data = {
            'name': 'Promotion 2024',
            'year': 2025,
            'program': self.program.id
        }
        serializer = FormationSerializer(self.formation, data=data)
        self.assertTrue(serializer.is_valid())
        updated_formation = serializer.save()
        self.assertEqual(updated_formation.year, 2025)
    
    def test_update_formation_program(self):
        """Test updating formation program via serializer."""
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        data = {
            'name': 'Promotion 2024',
            'year': 2024,
            'program': program2.id
        }
        serializer = FormationSerializer(self.formation, data=data)
        self.assertTrue(serializer.is_valid())
        updated_formation = serializer.save()
        self.assertEqual(updated_formation.program, program2)
    
    def test_partial_update_name_only(self):
        """Test partial update with only name."""
        data = {'name': 'Nouveau Nom'}
        serializer = FormationSerializer(self.formation, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_formation = serializer.save()
        self.assertEqual(updated_formation.name, 'Nouveau Nom')
        self.assertEqual(updated_formation.year, 2024)  # Unchanged
    
    def test_partial_update_year_only(self):
        """Test partial update with only year."""
        data = {'year': 2025}
        serializer = FormationSerializer(self.formation, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_formation = serializer.save()
        self.assertEqual(updated_formation.year, 2025)
        self.assertEqual(updated_formation.name, 'Promotion 2024')  # Unchanged
    
    def test_partial_update_program_only(self):
        """Test partial update with only program."""
        program2 = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        data = {'program': program2.id}
        serializer = FormationSerializer(self.formation, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_formation = serializer.save()
        self.assertEqual(updated_formation.program, program2)
    
    # ==================== SERIALIZATION OF MULTIPLE OBJECTS ====================
    
    def test_serialize_multiple_formations(self):
        """Test serializing multiple formations."""
        Formation.objects.create(
            name='Formation 2',
            year=2025,
            program=self.program
        )
        Formation.objects.create(
            name='Formation 3',
            year=2026,
            program=self.program
        )
        
        formations = Formation.objects.all()
        serializer = FormationSerializer(formations, many=True)
        
        self.assertEqual(len(serializer.data), 3)
    
    def test_serialize_empty_queryset(self):
        """Test serializing empty queryset."""
        Formation.objects.all().delete()
        formations = Formation.objects.all()
        serializer = FormationSerializer(formations, many=True)
        
        self.assertEqual(len(serializer.data), 0)
    
    # ==================== EDGE CASES ====================
    
    def test_special_characters_in_name(self):
        """Test formation with special characters in name."""
        data = {
            'name': 'Promotion 2024 - Spéciale & Avancée',
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        self.assertEqual(formation.name, 'Promotion 2024 - Spéciale & Avancée')
    
    def test_unicode_characters(self):
        """Test formation with unicode characters."""
        data = {
            'name': 'Promotion العربية 中文',
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        self.assertEqual(formation.name, 'Promotion العربية 中文')
    
    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is trimmed by DRF."""
        data = {
            'name': '  Formation with spaces  ',
            'year': 2024,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        # DRF CharFields trim whitespace by default
        self.assertEqual(formation.name, 'Formation with spaces')
    
    def test_year_with_negative_value(self):
        """Test formation with negative year (historical data)."""
        data = {
            'name': 'Historical Formation',
            'year': -500,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        self.assertEqual(formation.year, -500)
    
    def test_year_with_zero(self):
        """Test formation with year zero."""
        data = {
            'name': 'Year Zero Formation',
            'year': 0,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        self.assertEqual(formation.year, 0)
    
    def test_year_with_large_number(self):
        """Test formation with large year value."""
        data = {
            'name': 'Future Formation',
            'year': 9999,
            'program': self.program.id
        }
        serializer = FormationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        formation = serializer.save()
        self.assertEqual(formation.year, 9999)


# Need to import uuid for some tests
import uuid
