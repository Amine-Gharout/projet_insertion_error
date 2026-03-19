# student/tests/test_models.py
from django.test import TestCase
from django.db import IntegrityError
from student.models import Student
from datetime import date, timedelta
import uuid
import time


class StudentModelTest(TestCase):
    """Tests for the Student model."""
    
    def setUp(self):
        """Set up test data that runs before each test method."""
        self.student_data = {
            'matricule': 'E074001',
            'first_name': 'Mohammed',
            'last_name': 'Merzougui',
            'birth_date': date(2000, 1, 1)
        }
        self.student = Student.objects.create(**self.student_data)
    
    # ==================== CREATION TESTS ====================
    
    def test_student_creation_with_all_fields(self):
        """Test creating a student with all required fields."""
        self.assertEqual(self.student.matricule, 'E074001')
        self.assertEqual(self.student.first_name, 'Mohammed')
        self.assertEqual(self.student.last_name, 'Merzougui')
        self.assertEqual(self.student.birth_date, date(2000, 1, 1))
        self.assertIsNotNone(self.student.id)
        self.assertIsInstance(self.student.id, uuid.UUID)
    
    def test_student_creation_without_matricule(self):
        """Test creating a student without matricule (if null=True)."""
        student = Student.objects.create(
            first_name='Karim',
            last_name='Merzouk',
            birth_date=date(1999, 3, 15)
        )
        self.assertIsNotNone(student.id)
        self.assertIsNone(student.matricule)
    
    def test_student_creation_with_null_matricule(self):
        """Test explicitly setting matricule to None."""
        student = Student.objects.create(
            matricule=None,
            first_name='Amine',
            last_name='Gharout',
            birth_date=date(2001, 5, 20)
        )
        self.assertIsNone(student.matricule)
    
    def test_student_creation_with_blank_strings(self):
        """Test that blank strings are stored (not converted to None)."""
        student = Student.objects.create(
            matricule='',
            first_name='Test',
            last_name='User',
            birth_date=date(2000, 1, 1)
        )
        self.assertEqual(student.matricule, '')
    
    # ==================== UNIQUENESS TESTS ====================
    
    def test_matricule_unique_constraint(self):
        """Test that duplicate matricule raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                matricule='E074001',  # Duplicate
                first_name='Different',
                last_name='Person',
                birth_date=date(2001, 1, 1)
            )
    
    def test_multiple_null_matricules_allowed(self):
        """Test that multiple students can have null matricule."""
        student1 = Student.objects.create(
            matricule=None,
            first_name='Student',
            last_name='One',
            birth_date=date(2000, 1, 1)
        )
        student2 = Student.objects.create(
            matricule=None,
            first_name='Student',
            last_name='Two',
            birth_date=date(2000, 1, 1)
        )
        self.assertIsNone(student1.matricule)
        self.assertIsNone(student2.matricule)
        self.assertNotEqual(student1.id, student2.id)
    
    def test_different_matricules_allowed(self):
        """Test that different matricules can coexist."""
        student = Student.objects.create(
            matricule='E074002',
            first_name='Karim',
            last_name='Merzouk',
            birth_date=date(1999, 3, 15)
        )
        self.assertEqual(Student.objects.count(), 2)
    
    # ==================== UUID TESTS ====================
    
    def test_uuid_auto_generated(self):
        """Test that UUID is automatically generated."""
        student = Student.objects.create(
            matricule='E074003',
            first_name='Test',
            last_name='User',
            birth_date=date(2000, 1, 1)
        )
        self.assertIsNotNone(student.id)
        self.assertIsInstance(student.id, uuid.UUID)
    
    def test_uuid_unique_for_each_student(self):
        """Test that each student gets a unique UUID."""
        student1 = Student.objects.create(
            matricule='E074004',
            first_name='Student',
            last_name='One',
            birth_date=date(2000, 1, 1)
        )
        student2 = Student.objects.create(
            matricule='E074005',
            first_name='Student',
            last_name='Two',
            birth_date=date(2000, 1, 1)
        )
        self.assertNotEqual(student1.id, student2.id)
    
    # ==================== TIMESTAMP TESTS ====================
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set on creation."""
        self.assertIsNotNone(self.student.created_at)
    
    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set on creation."""
        self.assertIsNotNone(self.student.updated_at)
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when model is saved."""
        original_updated_at = self.student.updated_at
        
        # Wait a tiny bit to ensure timestamp changes
        time.sleep(0.01)
        self.student.first_name = 'Updated'
        self.student.save()
        
        self.assertNotEqual(self.student.updated_at, original_updated_at)
        self.assertGreater(self.student.updated_at, original_updated_at)
    
    def test_created_at_does_not_change_on_update(self):
        """Test that created_at remains unchanged on update."""
        original_created_at = self.student.created_at
        
        self.student.first_name = 'Updated'
        self.student.save()
        
        self.assertEqual(self.student.created_at, original_created_at)
    
    # ==================== STRING REPRESENTATION TESTS ====================
    
    def test_str_with_all_fields(self):
        """Test __str__ method with all fields present."""
        expected = 'E074001 - Mohammed Merzougui'
        self.assertEqual(str(self.student), expected)
    
    def test_str_without_matricule(self):
        """Test __str__ method when matricule is None."""
        student = Student.objects.create(
            matricule=None,
            first_name='NoMatricule',
            last_name='Student',
            birth_date=date(2000, 1, 1)
        )
        result = str(student)
        self.assertIn('NoMatricule', result)
        self.assertIn('Student', result)
    
    # ==================== FIELD VALIDATION TESTS ====================
    
    def test_matricule_max_length(self):
        """Test matricule field respects max_length."""
        long_matricule = 'E' * 21  # Exceeds max_length of 20
        student = Student(
            matricule=long_matricule,
            first_name='Test',
            last_name='User',
            birth_date=date(2000, 1, 1)
        )
        # This should raise ValidationError on full_clean()
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            student.full_clean()
    
    def test_first_name_max_length(self):
        """Test first_name field respects max_length."""
        long_name = 'A' * 61  # Exceeds max_length of 60
        student = Student(
            matricule='E074010',
            first_name=long_name,
            last_name='User',
            birth_date=date(2000, 1, 1)
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            student.full_clean()
    
    def test_last_name_max_length(self):
        """Test last_name field respects max_length."""
        long_name = 'B' * 61  # Exceeds max_length of 60
        student = Student(
            matricule='E074011',
            first_name='Test',
            last_name=long_name,
            birth_date=date(2000, 1, 1)
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            student.full_clean()
    
    def test_birth_date_with_valid_date(self):
        """Test birth_date accepts valid dates."""
        dates_to_test = [
            date(1950, 1, 1),
            date(2000, 12, 31),
            date.today(),
        ]
        for test_date in dates_to_test:
            student = Student.objects.create(
                matricule=f'E{test_date.year}',
                first_name='Test',
                last_name='User',
                birth_date=test_date
            )
            self.assertEqual(student.birth_date, test_date)
    
    def test_birth_date_future_date(self):
        """Test that future dates are accepted (validation should be in serializer)."""
        future_date = date.today() + timedelta(days=365)
        student = Student.objects.create(
            matricule='E999999',
            first_name='Future',
            last_name='Baby',
            birth_date=future_date
        )
        self.assertEqual(student.birth_date, future_date)
    
    # ==================== QUERY TESTS ====================
    
    def test_filter_by_matricule(self):
        """Test filtering students by matricule."""
        result = Student.objects.filter(matricule='E074001')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.student)
    
    def test_filter_by_first_name(self):
        """Test filtering students by first_name."""
        result = Student.objects.filter(first_name='Mohammed')
        self.assertEqual(result.count(), 1)
    
    def test_filter_by_last_name(self):
        """Test filtering students by last_name."""
        result = Student.objects.filter(last_name='Merzougui')
        self.assertEqual(result.count(), 1)
    
    def test_filter_by_birth_date(self):
        """Test filtering students by birth_date."""
        result = Student.objects.filter(birth_date=date(2000, 1, 1))
        self.assertEqual(result.count(), 1)
    
    def test_filter_null_matricule(self):
        """Test filtering students with null matricule."""
        Student.objects.create(
            matricule=None,
            first_name='Null',
            last_name='Matricule',
            birth_date=date(2000, 1, 1)
        )
        result = Student.objects.filter(matricule__isnull=True)
        self.assertEqual(result.count(), 1)
    
    def test_ordering_by_created_at(self):
        """Test ordering students by created_at."""
        time.sleep(0.01)  # Ensure different created_at timestamp
        student2 = Student.objects.create(
            matricule='E074002',
            first_name='Second',
            last_name='Student',
            birth_date=date(2000, 1, 1)
        )
        students = Student.objects.all().order_by('-created_at')
        self.assertEqual(students.first(), student2)
    
    # ==================== UPDATE TESTS ====================
    
    def test_update_matricule(self):
        """Test updating student's matricule."""
        self.student.matricule = 'E074999'
        self.student.save()
        self.student.refresh_from_db()
        self.assertEqual(self.student.matricule, 'E074999')
    
    def test_update_first_name(self):
        """Test updating student's first_name."""
        self.student.first_name = 'Updated'
        self.student.save()
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Updated')
    
    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        self.student.first_name = 'NewFirst'
        self.student.last_name = 'NewLast'
        self.student.matricule = 'E999999'
        self.student.save()
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'NewFirst')
        self.assertEqual(self.student.last_name, 'NewLast')
        self.assertEqual(self.student.matricule, 'E999999')
    
    # ==================== DELETE TESTS ====================
    
    def test_delete_student(self):
        """Test deleting a student."""
        student_id = self.student.id
        self.student.delete()
        self.assertEqual(Student.objects.filter(id=student_id).count(), 0)
    
    def test_bulk_delete(self):
        """Test bulk deleting students."""
        Student.objects.create(
            matricule='E074002',
            first_name='Student',
            last_name='Two',
            birth_date=date(2000, 1, 1)
        )
        Student.objects.all().delete()
        self.assertEqual(Student.objects.count(), 0)
    
    # ==================== EDGE CASES ====================
    
    def test_special_characters_in_names(self):
        """Test names with special characters."""
        student = Student.objects.create(
            matricule='E074020',
            first_name="Jean-Pierre",
            last_name="O'Brien-Smith",
            birth_date=date(2000, 1, 1)
        )
        self.assertEqual(student.first_name, "Jean-Pierre")
        self.assertEqual(student.last_name, "O'Brien-Smith")
    
    def test_unicode_characters_in_names(self):
        """Test names with Arabic/French characters."""
        student = Student.objects.create(
            matricule='E074021',
            first_name='محمد',
            last_name='Müller',
            birth_date=date(2000, 1, 1)
        )
        self.assertEqual(student.first_name, 'محمد')
        self.assertEqual(student.last_name, 'Müller')
    
    def test_empty_string_vs_none(self):
        """Test difference between empty string and None."""
        student1 = Student.objects.create(
            matricule='',
            first_name='Empty',
            last_name='String',
            birth_date=date(2000, 1, 1)
        )
        student2 = Student.objects.create(
            matricule=None,
            first_name='None',
            last_name='Value',
            birth_date=date(2000, 1, 1)
        )
        self.assertEqual(student1.matricule, '')
        self.assertIsNone(student2.matricule)
        self.assertNotEqual(student1.matricule, student2.matricule)