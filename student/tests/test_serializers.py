# student/tests/test_serializers.py
from django.test import TestCase
from student.models import Student
from student.serializer import StudentSerialzer
from datetime import date, timedelta


class StudentSerialzerTest(TestCase):
    """Tests for the StudentSerialzer."""
    
    def setUp(self):
        """Set up test data."""
        self.student_data = {
            'matricule': 'E074001',
            'first_name': 'Mohammed',
            'last_name': 'Merzougui',
            'birth_date': '2000-01-01'
        }
        self.student = Student.objects.create(
            matricule='E074001',
            first_name='Mohammed',
            last_name='Merzougui',
            birth_date=date(2000, 1, 1)
        )
    
    # ==================== SERIALIZATION TESTS ====================
    
    def test_serialize_student_with_all_fields(self):
        """Test serializing a student with all fields."""
        serializer = StudentSerialzer(self.student)
        data = serializer.data
        
        self.assertEqual(data['matricule'], 'E074001')
        self.assertEqual(data['first_name'], 'Mohammed')
        self.assertEqual(data['last_name'], 'Merzougui')
        self.assertEqual(data['birth_date'], '2000-01-01')
    
    def test_serialize_student_without_matricule(self):
        """Test serializing a student without matricule."""
        student = Student.objects.create(
            matricule=None,
            first_name='NoMatricule',
            last_name='Student',
            birth_date=date(2000, 1, 1)
        )
        serializer = StudentSerialzer(student)
        self.assertIsNone(serializer.data['matricule'])
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = StudentSerialzer(self.student)
        expected_fields = {'matricule', 'first_name', 'last_name', 'birth_date'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_serializer_excludes_id_and_timestamps(self):
        """Test that id and timestamps are not in serialized data."""
        serializer = StudentSerialzer(self.student)
        self.assertNotIn('id', serializer.data)
        self.assertNotIn('created_at', serializer.data)
        self.assertNotIn('updated_at', serializer.data)
    
    # ==================== DESERIALIZATION TESTS ====================
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid student data."""
        data = {
            'matricule': 'E074099',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-01-01'
        }
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        
        self.assertEqual(student.matricule, 'E074099')
        self.assertEqual(student.first_name, 'Test')
        self.assertEqual(student.last_name, 'User')
        self.assertEqual(student.birth_date, date(2000, 1, 1))
    
    def test_deserialize_without_matricule(self):
        """Test deserializing data without matricule."""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-01-01'
        }
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        self.assertIsNone(student.matricule)
    
    def test_deserialize_with_null_matricule(self):
        """Test deserializing with explicit null matricule."""
        data = self.student_data.copy()
        data['matricule'] = None
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        self.assertIsNone(student.matricule)
    
    def test_deserialize_with_empty_matricule(self):
        """Test deserializing with empty string matricule."""
        data = self.student_data.copy()
        data['matricule'] = ''
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        self.assertEqual(student.matricule, '')
    
    # ==================== VALIDATION TESTS ====================
    
    def test_missing_required_field_first_name(self):
        """Test validation fails when first_name is missing."""
        data = self.student_data.copy()
        del data['first_name']
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)
    
    def test_missing_required_field_last_name(self):
        """Test validation fails when last_name is missing."""
        data = self.student_data.copy()
        del data['last_name']
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)
    
    def test_missing_required_field_birth_date(self):
        """Test validation fails when birth_date is missing."""
        data = self.student_data.copy()
        del data['birth_date']
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('birth_date', serializer.errors)
    
    def test_invalid_date_format(self):
        """Test validation fails with invalid date format."""
        data = self.student_data.copy()
        data['birth_date'] = 'invalid-date'
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('birth_date', serializer.errors)
    
    def test_date_format_variations(self):
        """Test various valid date formats."""
        valid_dates = [
            '2000-01-01',
            '2000-12-31',
        ]
        for i, date_str in enumerate(valid_dates):
            data = {
                'matricule': f'E074{100+i}',
                'first_name': 'Test',
                'last_name': 'User',
                'birth_date': date_str
            }
            serializer = StudentSerialzer(data=data)
            self.assertTrue(serializer.is_valid(), f"Failed for date: {date_str}")
    
    def test_empty_string_for_required_fields(self):
        """Test that empty strings fail validation for required fields."""
        fields_to_test = ['first_name', 'last_name']
        for field in fields_to_test:
            data = self.student_data.copy()
            data[field] = ''
            serializer = StudentSerialzer(data=data)
            self.assertFalse(serializer.is_valid(), f"Should fail for empty {field}")
            self.assertIn(field, serializer.errors)
    
    def test_whitespace_only_for_text_fields(self):
        """Test that whitespace-only strings fail validation."""
        fields_to_test = ['first_name', 'last_name']
        for field in fields_to_test:
            data = self.student_data.copy()
            data[field] = '   '
            serializer = StudentSerialzer(data=data)
            self.assertFalse(serializer.is_valid(), f"Should fail for whitespace {field}")
    
    def test_very_long_matricule(self):
        """Test validation with matricule exceeding max_length."""
        data = self.student_data.copy()
        data['matricule'] = 'E' * 21  # Exceeds max_length of 20
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('matricule', serializer.errors)
    
    def test_very_long_first_name(self):
        """Test validation with first_name exceeding max_length."""
        data = self.student_data.copy()
        data['first_name'] = 'A' * 61  # Exceeds max_length of 60
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)
    
    def test_very_long_last_name(self):
        """Test validation with last_name exceeding max_length."""
        data = self.student_data.copy()
        data['last_name'] = 'B' * 61  # Exceeds max_length of 60
        serializer = StudentSerialzer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)
    
    # ==================== UPDATE TESTS ====================
    
    def test_partial_update_first_name(self):
        """Test partial update of first_name."""
        serializer = StudentSerialzer(
            self.student,
            data={'first_name': 'Updated'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_student = serializer.save()
        self.assertEqual(updated_student.first_name, 'Updated')
        self.assertEqual(updated_student.last_name, 'Merzougui')  # Unchanged
    
    def test_partial_update_matricule(self):
        """Test partial update of matricule."""
        serializer = StudentSerialzer(
            self.student,
            data={'matricule': 'E999999'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_student = serializer.save()
        self.assertEqual(updated_student.matricule, 'E999999')
    
    def test_full_update(self):
        """Test full update of all fields."""
        new_data = {
            'matricule': 'E999999',
            'first_name': 'NewFirst',
            'last_name': 'NewLast',
            'birth_date': '1999-12-31'
        }
        serializer = StudentSerialzer(self.student, data=new_data)
        self.assertTrue(serializer.is_valid())
        updated_student = serializer.save()
        
        self.assertEqual(updated_student.matricule, 'E999999')
        self.assertEqual(updated_student.first_name, 'NewFirst')
        self.assertEqual(updated_student.last_name, 'NewLast')
        self.assertEqual(updated_student.birth_date, date(1999, 12, 31))
    
    # ==================== EDGE CASES ====================
    
    def test_special_characters_in_data(self):
        """Test serialization with special characters."""
        data = {
            'matricule': 'E074-002',
            'first_name': "Jean-Pierre",
            'last_name': "O'Brien",
            'birth_date': '2000-01-01'
        }
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        self.assertEqual(student.first_name, "Jean-Pierre")
        self.assertEqual(student.last_name, "O'Brien")
    
    def test_unicode_characters(self):
        """Test serialization with unicode characters."""
        data = {
            'matricule': 'E074002',
            'first_name': 'محمد',
            'last_name': 'Müller',
            'birth_date': '2000-01-01'
        }
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        self.assertEqual(student.first_name, 'محمد')
    
    def test_serializer_with_extra_fields(self):
        """Test that extra fields are ignored."""
        data = {
            'matricule': 'E074200',
            'first_name': 'Test',
            'last_name': 'User',
            'birth_date': '2000-01-01',
            'extra_field': 'should be ignored'
        }
        serializer = StudentSerialzer(data=data)
        self.assertTrue(serializer.is_valid())
        student = serializer.save()
        self.assertFalse(hasattr(student, 'extra_field'))
    
    # ==================== MULTIPLE INSTANCE TESTS ====================
    
    def test_serialize_multiple_students(self):
        """Test serializing multiple students."""
        Student.objects.create(
            matricule='E074002',
            first_name='Karim',
            last_name='Merzouk',
            birth_date=date(1999, 3, 15)
        )
        students = Student.objects.all()
        serializer = StudentSerialzer(students, many=True)
        self.assertEqual(len(serializer.data), 2)
    
    def test_deserialize_multiple_students(self):
        """Test deserializing multiple students."""
        students_data = [
            {
                'matricule': 'E074002',
                'first_name': 'Karim',
                'last_name': 'Merzouk',
                'birth_date': '1999-03-15'
            },
            {
                'matricule': 'E074003',
                'first_name': 'Amine',
                'last_name': 'Gharout',
                'birth_date': '2001-05-20'
            }
        ]
        serializer = StudentSerialzer(data=students_data, many=True)
        self.assertTrue(serializer.is_valid())
        students = serializer.save()
        self.assertEqual(len(students), 2)