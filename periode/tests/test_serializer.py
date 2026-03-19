from django.test import TestCase
from curriculum_module.models import Periode
from curriculum.models import Curriculum
from curriculum_module.serializer import PeriodeSerializer
import uuid


class PeriodeSerializerTest(TestCase):
    """Tests for the PeriodeSerializer."""

    def setUp(self):
        """Set up test data."""
        self.curriculum = Curriculum.objects.create(
            title='Curriculum Informatique',
        )

        self.periode = Periode.objects.create(
            name='Semestre 1',
            curriculum=self.curriculum,
            credits=30,
            rank=1,
            moyenne=14.5,
        )

    # ==================== SERIALIZATION TESTS ====================

    def test_serialize_periode_contains_all_fields(self):
        """Test that serializer includes all expected fields (fields='__all__')."""
        serializer = PeriodeSerializer(self.periode)
        data = serializer.data

        expected_fields = {'id', 'name', 'curriculum', 'credits', 'rank', 'moyenne', 'created_at'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serialize_name(self):
        """Test that name is correctly serialized."""
        serializer = PeriodeSerializer(self.periode)
        self.assertEqual(serializer.data['name'], 'Semestre 1')

    def test_serialize_credits(self):
        """Test that credits is correctly serialized."""
        serializer = PeriodeSerializer(self.periode)
        self.assertEqual(serializer.data['credits'], 30)

    def test_serialize_rank(self):
        """Test that rank is correctly serialized."""
        serializer = PeriodeSerializer(self.periode)
        self.assertEqual(serializer.data['rank'], 1)

    def test_serialize_moyenne(self):
        """Test that moyenne is correctly serialized."""
        serializer = PeriodeSerializer(self.periode)
        self.assertEqual(serializer.data['moyenne'], 14.5)

    def test_serialize_curriculum_returns_uuid(self):
        """Test that curriculum field returns its UUID."""
        serializer = PeriodeSerializer(self.periode)
        self.assertEqual(serializer.data['curriculum'], self.curriculum.id)

    def test_serialize_id_is_uuid(self):
        """Test that id field is a UUID."""
        serializer = PeriodeSerializer(self.periode)
        self.assertIsInstance(serializer.data['id'], uuid.UUID)

    def test_serialize_created_at_is_present(self):
        """Test that created_at is included in serialized data."""
        serializer = PeriodeSerializer(self.periode)
        self.assertIsNotNone(serializer.data['created_at'])

    def test_serialize_nullable_fields_as_none(self):
        """Test serializing a periode with null rank and moyenne."""
        periode = Periode.objects.create(
            name='Semestre Null',
            curriculum=self.curriculum,
            credits=20,
        )
        serializer = PeriodeSerializer(periode)
        self.assertIsNone(serializer.data['rank'])
        self.assertIsNone(serializer.data['moyenne'])

    # ==================== DESERIALIZATION TESTS ====================

    def test_deserialize_valid_data_with_all_fields(self):
        """Test deserializing valid data including optional fields."""
        data = {
            'name': 'Semestre 2',
            'curriculum': str(self.curriculum.id),
            'credits': 28,
            'rank': 2,
            'moyenne': 13.0,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        periode = serializer.save()

        self.assertEqual(periode.name, 'Semestre 2')
        self.assertEqual(periode.credits, 28)
        self.assertEqual(periode.rank, 2)
        self.assertEqual(periode.moyenne, 13.0)
        self.assertEqual(periode.curriculum, self.curriculum)

    def test_deserialize_valid_data_without_optional_fields(self):
        """Test deserializing data without rank and moyenne."""
        data = {
            'name': 'Semestre 3',
            'curriculum': str(self.curriculum.id),
            'credits': 25,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        periode = serializer.save()

        self.assertIsNone(periode.rank)
        self.assertIsNone(periode.moyenne)

    # ==================== VALIDATION TESTS ====================

    def test_invalid_without_name(self):
        """Test that serializer rejects missing name."""
        data = {
            'curriculum': str(self.curriculum.id),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_invalid_with_empty_name(self):
        """Test that serializer rejects empty name."""
        data = {
            'name': '',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_invalid_without_credits(self):
        """Test that serializer rejects missing credits."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('credits', serializer.errors)

    def test_invalid_without_curriculum(self):
        """Test that serializer rejects missing curriculum."""
        data = {
            'name': 'Semestre Test',
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('curriculum', serializer.errors)

    def test_invalid_with_nonexistent_curriculum(self):
        """Test that serializer rejects a non-existent curriculum UUID."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(uuid.uuid4()),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('curriculum', serializer.errors)

    def test_invalid_name_too_long(self):
        """Test that serializer rejects name longer than 100 characters."""
        data = {
            'name': 'A' * 101,
            'curriculum': str(self.curriculum.id),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_valid_name_at_max_length(self):
        """Test that serializer accepts name exactly at 100 characters."""
        data = {
            'name': 'A' * 100,
            'curriculum': str(self.curriculum.id),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_credits_as_text(self):
        """Test that serializer rejects non-numeric credits."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
            'credits': 'not-a-number',
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('credits', serializer.errors)

    def test_credits_as_string_number_is_converted(self):
        """Test that DRF converts string number to int for credits."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
            'credits': '20',
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        periode = serializer.save()
        self.assertEqual(periode.credits, 20)
        self.assertIsInstance(periode.credits, int)

    def test_invalid_rank_as_text(self):
        """Test that serializer rejects non-numeric rank."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
            'rank': 'first',
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rank', serializer.errors)

    def test_invalid_moyenne_as_text(self):
        """Test that serializer rejects non-numeric moyenne."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
            'moyenne': 'high',
        }
        serializer = PeriodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('moyenne', serializer.errors)

    def test_rank_null_is_valid(self):
        """Test that null rank is accepted."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
            'rank': None,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_moyenne_null_is_valid(self):
        """Test that null moyenne is accepted."""
        data = {
            'name': 'Semestre Test',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
            'moyenne': None,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # ==================== UPDATE TESTS ====================

    def test_full_update(self):
        """Test full update via serializer."""
        data = {
            'name': 'Semestre 1 Updated',
            'curriculum': str(self.curriculum.id),
            'credits': 35,
            'rank': 1,
            'moyenne': 15.0,
        }
        serializer = PeriodeSerializer(self.periode, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.name, 'Semestre 1 Updated')
        self.assertEqual(updated.credits, 35)
        self.assertEqual(updated.moyenne, 15.0)

    def test_partial_update_name(self):
        """Test partial update of name only."""
        serializer = PeriodeSerializer(self.periode, data={'name': 'Nouveau Nom'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.name, 'Nouveau Nom')
        self.assertEqual(updated.credits, 30)  # Unchanged

    def test_partial_update_credits(self):
        """Test partial update of credits only."""
        serializer = PeriodeSerializer(self.periode, data={'credits': 15}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.credits, 15)
        self.assertEqual(updated.name, 'Semestre 1')  # Unchanged

    def test_partial_update_rank(self):
        """Test partial update of rank."""
        serializer = PeriodeSerializer(self.periode, data={'rank': 3}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.rank, 3)

    def test_partial_update_moyenne(self):
        """Test partial update of moyenne."""
        serializer = PeriodeSerializer(self.periode, data={'moyenne': 17.5}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.moyenne, 17.5)

    def test_partial_update_set_rank_to_null(self):
        """Test partial update setting rank to null."""
        serializer = PeriodeSerializer(self.periode, data={'rank': None}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertIsNone(updated.rank)

    # ==================== MULTIPLE OBJECTS ====================

    def test_serialize_multiple_periodes(self):
        """Test serializing multiple periodes."""
        Periode.objects.create(name='Semestre 2', curriculum=self.curriculum, credits=28)
        Periode.objects.create(name='Semestre 3', curriculum=self.curriculum, credits=20)

        periodes = Periode.objects.all()
        serializer = PeriodeSerializer(periodes, many=True)
        self.assertEqual(len(serializer.data), 3)

    def test_serialize_empty_queryset(self):
        """Test serializing an empty queryset."""
        Periode.objects.all().delete()
        serializer = PeriodeSerializer(Periode.objects.all(), many=True)
        self.assertEqual(len(serializer.data), 0)

    # ==================== EDGE CASES ====================

    def test_special_characters_in_name(self):
        """Test serializer handles special characters in name."""
        data = {
            'name': 'Semestre & Spéciale - Avancée',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        periode = serializer.save()
        self.assertEqual(periode.name, 'Semestre & Spéciale - Avancée')

    def test_unicode_in_name(self):
        """Test serializer handles unicode in name."""
        data = {
            'name': 'الفصل الأول',
            'curriculum': str(self.curriculum.id),
            'credits': 20,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_credits_zero_is_valid(self):
        """Test that credits = 0 is valid."""
        data = {
            'name': 'Zero Credits',
            'curriculum': str(self.curriculum.id),
            'credits': 0,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_moyenne_zero_is_valid(self):
        """Test that moyenne = 0.0 is valid."""
        data = {
            'name': 'Zero Moyenne',
            'curriculum': str(self.curriculum.id),
            'credits': 10,
            'moyenne': 0.0,
        }
        serializer = PeriodeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)