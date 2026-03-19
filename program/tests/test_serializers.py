# program/tests/test_serializers.py
from django.test import TestCase
from program.models import Program
from program.serializer import ProgramSerializer


class ProgramSerializerTest(TestCase):
    """Tests for the ProgramSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.program_data = {
            'title': 'Informatique',
            'code': 'INFO101',
            'description': 'Programme en informatique',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        self.program = Program.objects.create(**self.program_data)
    
    # ==================== SERIALIZATION TESTS ====================
    
    def test_serialize_program_with_all_fields(self):
        """Test serializing a program with all fields."""
        serializer = ProgramSerializer(self.program)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Informatique')
        self.assertEqual(data['code'], 'INFO101')
        self.assertEqual(data['description'], 'Programme en informatique')
        self.assertEqual(data['cycle'], 'Licence')
        self.assertEqual(data['diploma'], 'Licence en Informatique')
    
    def test_serialize_program_without_description(self):
        """Test serializing a program without description."""
        program = Program.objects.create(
            title='Mathématiques',
            code='MATH201',
            description=None,
            cycle='Master',
            diploma='Master en Mathématiques'
        )
        serializer = ProgramSerializer(program)
        self.assertIsNone(serializer.data['description'])
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = ProgramSerializer(self.program)
        expected_fields = {'title', 'code', 'description', 'cycle', 'diploma'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_serializer_excludes_id_and_timestamps(self):
        """Test that id and timestamps are not in serialized data."""
        serializer = ProgramSerializer(self.program)
        self.assertNotIn('id', serializer.data)
        self.assertNotIn('created_at', serializer.data)
        self.assertNotIn('updated_at', serializer.data)
    
    # ==================== DESERIALIZATION TESTS ====================
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid program data."""
        data = {
            'title': 'Génie Logiciel',
            'code': 'GL101',
            'description': 'Programme de génie logiciel',
            'cycle': 'Master',
            'diploma': 'Master en Génie Logiciel'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        
        self.assertEqual(program.title, 'Génie Logiciel')
        self.assertEqual(program.code, 'GL101')
        self.assertEqual(program.description, 'Programme de génie logiciel')
        self.assertEqual(program.cycle, 'Master')
        self.assertEqual(program.diploma, 'Master en Génie Logiciel')
    
    def test_deserialize_without_description(self):
        """Test deserializing data without description."""
        data = {
            'title': 'Physique',
            'code': 'PHYS301',
            'cycle': 'Doctorat',
            'diploma': 'Doctorat en Physique'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        self.assertIsNone(program.description)
    
    def test_deserialize_with_null_description(self):
        """Test deserializing with explicit null description."""
        data = {
            'title': 'Chimie',
            'code': 'CHEM401',
            'description': None,
            'cycle': 'Licence',
            'diploma': 'Licence en Chimie'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        self.assertIsNone(program.description)
    
    def test_deserialize_with_empty_description(self):
        """Test deserializing with empty string description."""
        data = {
            'title': 'Biologie',
            'code': 'BIO501',
            'description': '',
            'cycle': 'Master',
            'diploma': 'Master en Biologie'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        self.assertEqual(program.description, '')
    
    # ==================== VALIDATION TESTS ====================
    
    def test_invalid_without_title(self):
        """Test that serializer is invalid without title."""
        data = {
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_invalid_without_code(self):
        """Test that serializer is invalid without code."""
        data = {
            'title': 'Test Program',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_invalid_without_cycle(self):
        """Test that serializer is invalid without cycle."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cycle', serializer.errors)
    
    def test_invalid_without_diploma(self):
        """Test that serializer is invalid without diploma."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'Licence'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('diploma', serializer.errors)
    
    def test_invalid_with_duplicate_title(self):
        """Test that serializer rejects duplicate title."""
        data = {
            'title': 'Informatique',  # Already exists
            'code': 'DIFF001',
            'cycle': 'Master',
            'diploma': 'Master en Informatique'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_invalid_with_duplicate_code(self):
        """Test that serializer rejects duplicate code."""
        data = {
            'title': 'Another Program',
            'code': 'INFO101',  # Already exists
            'cycle': 'Master',
            'diploma': 'Master Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_invalid_with_empty_title(self):
        """Test that serializer rejects empty title."""
        data = {
            'title': '',
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_invalid_with_empty_code(self):
        """Test that serializer rejects empty code."""
        data = {
            'title': 'Test Program',
            'code': '',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_invalid_with_empty_cycle(self):
        """Test that serializer rejects empty cycle."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': '',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cycle', serializer.errors)
    
    def test_invalid_with_empty_diploma(self):
        """Test that serializer rejects empty diploma."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': ''
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('diploma', serializer.errors)
    
    def test_invalid_with_title_too_long(self):
        """Test that serializer rejects title longer than 100 characters."""
        data = {
            'title': 'A' * 101,  # 101 characters
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_valid_with_title_at_max_length(self):
        """Test that serializer accepts title at max length (100 chars)."""
        data = {
            'title': 'A' * 100,  # Exactly 100 characters
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_with_code_too_long(self):
        """Test that serializer rejects code longer than 20 characters."""
        data = {
            'title': 'Test Program',
            'code': 'A' * 21,  # 21 characters
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)
    
    def test_valid_with_code_at_max_length(self):
        """Test that serializer accepts code at max length (20 chars)."""
        data = {
            'title': 'Test Program',
            'code': 'A' * 20,  # Exactly 20 characters
            'cycle': 'Licence',
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_with_cycle_too_long(self):
        """Test that serializer rejects cycle longer than 20 characters."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'A' * 21,  # 21 characters
            'diploma': 'Test Diploma'
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cycle', serializer.errors)
    
    def test_invalid_with_diploma_too_long(self):
        """Test that serializer rejects diploma longer than 50 characters."""
        data = {
            'title': 'Test Program',
            'code': 'TEST001',
            'cycle': 'Licence',
            'diploma': 'A' * 51  # 51 characters
        }
        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('diploma', serializer.errors)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_program_title(self):
        """Test updating program title via serializer."""
        data = {
            'title': 'Informatique Avancée',
            'code': 'INFO101',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        serializer = ProgramSerializer(self.program, data=data)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.title, 'Informatique Avancée')
    
    def test_update_program_code(self):
        """Test updating program code via serializer."""
        data = {
            'title': 'Informatique',
            'code': 'INFO102',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        serializer = ProgramSerializer(self.program, data=data)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.code, 'INFO102')
    
    def test_update_program_description(self):
        """Test updating program description via serializer."""
        data = {
            'title': 'Informatique',
            'code': 'INFO101',
            'description': 'Nouvelle description',
            'cycle': 'Licence',
            'diploma': 'Licence en Informatique'
        }
        serializer = ProgramSerializer(self.program, data=data)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.description, 'Nouvelle description')
    
    def test_update_program_cycle(self):
        """Test updating program cycle via serializer."""
        data = {
            'title': 'Informatique',
            'code': 'INFO101',
            'cycle': 'Master',
            'diploma': 'Licence en Informatique'
        }
        serializer = ProgramSerializer(self.program, data=data)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.cycle, 'Master')
    
    def test_update_program_diploma(self):
        """Test updating program diploma via serializer."""
        data = {
            'title': 'Informatique',
            'code': 'INFO101',
            'cycle': 'Licence',
            'diploma': 'Master en Informatique'
        }
        serializer = ProgramSerializer(self.program, data=data)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.diploma, 'Master en Informatique')
    
    def test_partial_update_title_only(self):
        """Test partial update with only title."""
        data = {'title': 'Nouveau Titre'}
        serializer = ProgramSerializer(self.program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.title, 'Nouveau Titre')
        self.assertEqual(updated_program.code, 'INFO101')  # Unchanged
    
    def test_partial_update_code_only(self):
        """Test partial update with only code."""
        data = {'code': 'NEW001'}
        serializer = ProgramSerializer(self.program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.code, 'NEW001')
        self.assertEqual(updated_program.title, 'Informatique')  # Unchanged
    
    def test_partial_update_description_only(self):
        """Test partial update with only description."""
        data = {'description': 'Nouvelle description'}
        serializer = ProgramSerializer(self.program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.description, 'Nouvelle description')
    
    def test_partial_update_cycle_only(self):
        """Test partial update with only cycle."""
        data = {'cycle': 'Doctorat'}
        serializer = ProgramSerializer(self.program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.cycle, 'Doctorat')
    
    def test_partial_update_diploma_only(self):
        """Test partial update with only diploma."""
        data = {'diploma': 'Doctorat en Informatique'}
        serializer = ProgramSerializer(self.program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_program = serializer.save()
        self.assertEqual(updated_program.diploma, 'Doctorat en Informatique')
    
    # ==================== SERIALIZATION OF MULTIPLE OBJECTS ====================
    
    def test_serialize_multiple_programs(self):
        """Test serializing multiple programs."""
        Program.objects.create(
            title='Program 2',
            code='PRG002',
            cycle='Master',
            diploma='Master Diploma'
        )
        Program.objects.create(
            title='Program 3',
            code='PRG003',
            cycle='Doctorat',
            diploma='Doctorat Diploma'
        )
        
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        
        self.assertEqual(len(serializer.data), 3)
    
    def test_serialize_empty_queryset(self):
        """Test serializing empty queryset."""
        Program.objects.all().delete()
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        
        self.assertEqual(len(serializer.data), 0)
    
    # ==================== EDGE CASES ====================
    
    def test_special_characters_in_title(self):
        """Test program with special characters in title."""
        data = {
            'title': 'C++ & C# Programming',
            'code': 'CPP001',
            'description': 'Description <test>',
            'cycle': 'Licence',
            'diploma': 'Licence en Programmation'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        self.assertEqual(program.title, 'C++ & C# Programming')
    
    def test_unicode_characters(self):
        """Test program with unicode characters."""
        data = {
            'title': 'Mathématiques العربية',
            'code': 'MATH001',
            'description': 'Description avec accents éèê',
            'cycle': 'Licence',
            'diploma': 'Licence en Mathématiques'
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        self.assertEqual(program.title, 'Mathématiques العربية')
    
    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is trimmed by DRF."""
        data = {
            'title': '  Program with spaces  ',
            'code': 'SPACE001',
            'cycle': '  Licence  ',
            'diploma': '  Test Diploma  '
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        program = serializer.save()
        # DRF CharFields trim whitespace by default
        self.assertEqual(program.title, 'Program with spaces')
        self.assertEqual(program.cycle, 'Licence')
        self.assertEqual(program.diploma, 'Test Diploma')
