from django.test import TestCase
from curriculum.models import Curriculum
from student.models import Student
from formation.models import Formation
from curriculum.serializer import CurriculumSerializer
import uuid


class CurriculumSerializerTest(TestCase):
    """Tests for the CurriculumSerializer."""

    def setUp(self):
        """Set up test data."""
        self.student = Student.objects.create(
            first_name='Mohammed',
            last_name='Merzougui',
            matricule='E074001',
        )
        self.student2 = Student.objects.create(
            first_name='Karim',
            last_name='Merzouk',
            matricule='E074002',
        )
        self.formation = Formation.objects.create(
            name='Promotion 2024',
            year=2024,
        )
        self.formation2 = Formation.objects.create(
            name='Promotion 2025',
            year=2025,
        )

        self.curriculum = Curriculum.objects.create(
            student=self.student,
            formation=self.formation,
            section='A',
            group='G1',
            status='active',
            rank=1,
            moyenne_finale=14.5,
            moyenne_rachat=12.0,
            moyenne_concours=15.0,
        )

    # ==================== SERIALIZATION TESTS ====================

    def test_serializer_contains_all_fields(self):
        """Test serializer includes all expected fields (fields='__all__')."""
        serializer = CurriculumSerializer(self.curriculum)
        expected_fields = {
            'id', 'section', 'group', 'student', 'formation',
            'moyenne_rachat', 'moyenne_finale', 'moyenne_concours',
            'status', 'rank', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_serialize_section(self):
        """Test section is correctly serialized."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['section'], 'A')

    def test_serialize_group(self):
        """Test group is correctly serialized."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['group'], 'G1')

    def test_serialize_status(self):
        """Test status is correctly serialized."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['status'], 'active')

    def test_serialize_rank(self):
        """Test rank is correctly serialized."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['rank'], 1)

    def test_serialize_moyenne_fields(self):
        """Test all moyenne fields are correctly serialized."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['moyenne_finale'], 14.5)
        self.assertEqual(serializer.data['moyenne_rachat'], 12.0)
        self.assertEqual(serializer.data['moyenne_concours'], 15.0)

    def test_serialize_student_returns_uuid(self):
        """Test student field returns UUID."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['student'], self.student.id)

    def test_serialize_formation_returns_uuid(self):
        """Test formation field returns UUID."""
        serializer = CurriculumSerializer(self.curriculum)
        self.assertEqual(serializer.data['formation'], self.formation.id)

    def test_serialize_nullable_fields_as_none(self):
        """Test nullable fields serialize as None when not set."""
        curriculum = Curriculum.objects.create(
            student=self.student2,
            formation=self.formation,
            status='active',
        )
        serializer = CurriculumSerializer(curriculum)
        self.assertIsNone(serializer.data['section'])
        self.assertIsNone(serializer.data['group'])
        self.assertIsNone(serializer.data['rank'])
        self.assertIsNone(serializer.data['moyenne_finale'])
        self.assertIsNone(serializer.data['moyenne_rachat'])
        self.assertIsNone(serializer.data['moyenne_concours'])

    # ==================== DESERIALIZATION TESTS ====================

    def test_deserialize_valid_data_all_fields(self):
        """Test deserializing valid data with all fields."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'section': 'B',
            'group': 'G2',
            'status': 'active',
            'rank': 2,
            'moyenne_finale': 13.0,
            'moyenne_rachat': 11.0,
            'moyenne_concours': 14.0,
        }
        serializer = CurriculumSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        curriculum = serializer.save()
        self.assertEqual(curriculum.section, 'B')
        self.assertEqual(curriculum.status, 'active')
        self.assertEqual(curriculum.moyenne_finale, 13.0)

    def test_deserialize_valid_data_required_fields_only(self):
        """Test deserializing with only required fields."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        curriculum = serializer.save()
        self.assertIsNone(curriculum.section)
        self.assertIsNone(curriculum.rank)

    # ==================== VALIDATION TESTS ====================

    def test_invalid_without_student(self):
        """Test serializer rejects missing student."""
        data = {
            'formation': str(self.formation2.id),
            'status': 'active',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('student', serializer.errors)

    def test_invalid_without_formation(self):
        """Test serializer rejects missing formation."""
        data = {
            'student': str(self.student2.id),
            'status': 'active',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('formation', serializer.errors)

    def test_invalid_without_status(self):
        """Test serializer rejects missing status."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_invalid_with_empty_status(self):
        """Test serializer rejects empty status."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': '',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_invalid_with_nonexistent_student(self):
        """Test serializer rejects non-existent student UUID."""
        data = {
            'student': str(uuid.uuid4()),
            'formation': str(self.formation2.id),
            'status': 'active',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('student', serializer.errors)

    def test_invalid_with_nonexistent_formation(self):
        """Test serializer rejects non-existent formation UUID."""
        data = {
            'student': str(self.student2.id),
            'formation': str(uuid.uuid4()),
            'status': 'active',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('formation', serializer.errors)

    def test_invalid_duplicate_student_formation(self):
        """Test serializer rejects duplicate student+formation combination."""
        data = {
            'student': str(self.student.id),
            'formation': str(self.formation.id),  # Already exists
            'status': 'active',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_status_too_long(self):
        """Test serializer rejects status longer than 20 characters."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'A' * 21,
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_invalid_moyenne_as_text(self):
        """Test serializer rejects non-numeric moyenne_finale."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'moyenne_finale': 'high',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('moyenne_finale', serializer.errors)

    def test_invalid_rank_as_text(self):
        """Test serializer rejects non-numeric rank."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'rank': 'first',
        }
        serializer = CurriculumSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rank', serializer.errors)

    def test_null_rank_is_valid(self):
        """Test null rank is accepted."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'rank': None,
        }
        serializer = CurriculumSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_null_moyennes_are_valid(self):
        """Test null moyenne fields are accepted."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'moyenne_finale': None,
            'moyenne_rachat': None,
            'moyenne_concours': None,
        }
        serializer = CurriculumSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # ==================== UPDATE TESTS ====================

    def test_full_update(self):
        """Test full update via serializer."""
        data = {
            'student': str(self.student.id),
            'formation': str(self.formation.id),
            'section': 'C',
            'group': 'G3',
            'status': 'graduated',
            'rank': 2,
            'moyenne_finale': 16.0,
            'moyenne_rachat': None,
            'moyenne_concours': 17.0,
        }
        serializer = CurriculumSerializer(self.curriculum, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.status, 'graduated')
        self.assertEqual(updated.section, 'C')
        self.assertEqual(updated.moyenne_finale, 16.0)

    def test_partial_update_status(self):
        """Test partial update of status."""
        serializer = CurriculumSerializer(self.curriculum, data={'status': 'inactive'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.status, 'inactive')
        self.assertEqual(updated.section, 'A')  # Unchanged

    def test_partial_update_rank(self):
        """Test partial update of rank."""
        serializer = CurriculumSerializer(self.curriculum, data={'rank': 10}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.rank, 10)

    def test_partial_update_moyenne_finale(self):
        """Test partial update of moyenne_finale."""
        serializer = CurriculumSerializer(self.curriculum, data={'moyenne_finale': 18.0}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.moyenne_finale, 18.0)

    def test_partial_update_set_section_to_null(self):
        """Test partial update setting section to null."""
        serializer = CurriculumSerializer(self.curriculum, data={'section': None}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertIsNone(updated.section)

    # ==================== MULTIPLE OBJECTS ====================

    def test_serialize_multiple_curriculums(self):
        """Test serializing multiple curriculums."""
        Curriculum.objects.create(student=self.student2, formation=self.formation, status='active')
        serializer = CurriculumSerializer(Curriculum.objects.all(), many=True)
        self.assertEqual(len(serializer.data), 2)

    def test_serialize_empty_queryset(self):
        """Test serializing empty queryset."""
        Curriculum.objects.all().delete()
        serializer = CurriculumSerializer(Curriculum.objects.all(), many=True)
        self.assertEqual(len(serializer.data), 0)

    # ==================== EDGE CASES ====================

    def test_moyenne_zero_is_valid(self):
        """Test that 0.0 is a valid moyenne value."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'moyenne_finale': 0.0,
        }
        serializer = CurriculumSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rank_zero_is_valid(self):
        """Test that rank = 0 is valid."""
        data = {
            'student': str(self.student2.id),
            'formation': str(self.formation2.id),
            'status': 'active',
            'rank': 0,
        }
        serializer = CurriculumSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)