from django.test import TestCase
from django.db import IntegrityError
from curriculum_module.models import Periode
from curriculum.models import Curriculum
import uuid


class PeriodeModelTest(TestCase):
    """Tests for the Periode model."""

    def setUp(self):
        """Set up test data before each test."""
        self.curriculum = Curriculum.objects.create(
            # Adjust fields to match your actual Curriculum model
            title='Curriculum Informatique',
        )

        self.periode_data = {
            'name': 'Semestre 1',
            'curriculum': self.curriculum,
            'credits': 30,
            'rank': 1,
            'moyenne': 14.5,
        }
        self.periode = Periode.objects.create(**self.periode_data)

    # ==================== CREATION TESTS ====================

    def test_periode_creation_with_all_fields(self):
        """Test creating a periode with all fields."""
        self.assertEqual(self.periode.name, 'Semestre 1')
        self.assertEqual(self.periode.credits, 30)
        self.assertEqual(self.periode.rank, 1)
        self.assertEqual(self.periode.moyenne, 14.5)
        self.assertEqual(self.periode.curriculum, self.curriculum)
        self.assertIsNotNone(self.periode.id)
        self.assertIsInstance(self.periode.id, uuid.UUID)

    def test_periode_creation_without_optional_fields(self):
        """Test creating a periode without optional fields (rank, moyenne)."""
        periode = Periode.objects.create(
            name='Semestre 2',
            curriculum=self.curriculum,
            credits=25,
        )
        self.assertIsNone(periode.rank)
        self.assertIsNone(periode.moyenne)

    def test_periode_creation_with_rank_none(self):
        """Test that rank is nullable."""
        periode = Periode.objects.create(
            name='Semestre Test',
            curriculum=self.curriculum,
            credits=20,
            rank=None,
        )
        self.assertIsNone(periode.rank)

    def test_periode_creation_with_moyenne_none(self):
        """Test that moyenne is nullable."""
        periode = Periode.objects.create(
            name='Semestre Test',
            curriculum=self.curriculum,
            credits=20,
            moyenne=None,
        )
        self.assertIsNone(periode.moyenne)

    def test_multiple_periodes_same_curriculum(self):
        """Test multiple periodes can belong to the same curriculum."""
        periode2 = Periode.objects.create(
            name='Semestre 2',
            curriculum=self.curriculum,
            credits=28,
            rank=2,
        )
        self.assertEqual(self.periode.curriculum, periode2.curriculum)
        self.assertNotEqual(self.periode.id, periode2.id)

    # ==================== UUID TESTS ====================

    def test_uuid_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        self.assertIsNotNone(self.periode.id)
        self.assertIsInstance(self.periode.id, uuid.UUID)

    def test_uuid_is_unique(self):
        """Test that each periode gets a unique UUID."""
        periode2 = Periode.objects.create(
            name='Semestre 2',
            curriculum=self.curriculum,
            credits=25,
        )
        self.assertNotEqual(self.periode.id, periode2.id)

    def test_uuid_is_not_editable(self):
        """Test that UUID field is not editable."""
        field = Periode._meta.get_field('id')
        self.assertFalse(field.editable)

    # ==================== TIMESTAMP TESTS ====================

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set on creation."""
        self.assertIsNotNone(self.periode.created_at)

    def test_created_at_does_not_change_on_save(self):
        """Test that created_at does not change on subsequent saves."""
        original_created_at = self.periode.created_at
        self.periode.name = 'Updated Name'
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.created_at, original_created_at)

    # ==================== STRING REPRESENTATION TESTS ====================

    def test_str_representation(self):
        """Test the __str__ method returns expected format."""
        expected = f'{self.curriculum} - Semestre 1 (30 credits)'
        self.assertEqual(str(self.periode), expected)

    def test_str_with_different_credits(self):
        """Test __str__ with different credit values."""
        periode = Periode.objects.create(
            name='Module A',
            curriculum=self.curriculum,
            credits=6,
        )
        expected = f'{self.curriculum} - Module A (6 credits)'
        self.assertEqual(str(periode), expected)

    # ==================== META OPTIONS TESTS ====================

    def test_meta_ordering(self):
        """Test that periodes are ordered by curriculum then rank."""
        Periode.objects.create(name='Semestre 3', curriculum=self.curriculum, credits=20, rank=3)
        Periode.objects.create(name='Semestre 0', curriculum=self.curriculum, credits=15, rank=None)

        periodes = list(Periode.objects.filter(curriculum=self.curriculum).exclude(rank=None))
        ranks = [p.rank for p in periodes]
        self.assertEqual(ranks, sorted(ranks))

    def test_meta_verbose_name(self):
        """Test verbose_name Meta option."""
        self.assertEqual(Periode._meta.verbose_name, 'Periode')

    def test_meta_verbose_name_plural(self):
        """Test verbose_name_plural Meta option."""
        self.assertEqual(Periode._meta.verbose_name_plural, 'Periodes')

    def test_meta_db_table(self):
        """Test db_table Meta option."""
        self.assertEqual(Periode._meta.db_table, 'periode')

    # ==================== FIELD CONSTRAINTS TESTS ====================

    def test_name_max_length(self):
        """Test name field max_length is 100."""
        field = Periode._meta.get_field('name')
        self.assertEqual(field.max_length, 100)

    def test_credits_is_integer_field(self):
        """Test that credits is an IntegerField."""
        field = Periode._meta.get_field('credits')
        self.assertEqual(field.get_internal_type(), 'IntegerField')

    def test_rank_is_integer_field(self):
        """Test that rank is an IntegerField."""
        field = Periode._meta.get_field('rank')
        self.assertEqual(field.get_internal_type(), 'IntegerField')

    def test_rank_is_nullable(self):
        """Test that rank allows null."""
        field = Periode._meta.get_field('rank')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_moyenne_is_float_field(self):
        """Test that moyenne is a FloatField."""
        field = Periode._meta.get_field('moyenne')
        self.assertEqual(field.get_internal_type(), 'FloatField')

    def test_moyenne_is_nullable(self):
        """Test that moyenne allows null."""
        field = Periode._meta.get_field('moyenne')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_curriculum_is_foreign_key(self):
        """Test that curriculum is a ForeignKey."""
        field = Periode._meta.get_field('curriculum')
        self.assertEqual(field.get_internal_type(), 'ForeignKey')

    def test_curriculum_related_name(self):
        """Test that curriculum has correct related_name."""
        field = Periode._meta.get_field('curriculum')
        self.assertEqual(field.remote_field.related_name, 'periode')

    def test_curriculum_on_delete_cascade(self):
        """Test that curriculum ForeignKey uses CASCADE on_delete."""
        from django.db.models import CASCADE
        field = Periode._meta.get_field('curriculum')
        self.assertEqual(field.remote_field.on_delete, CASCADE)

    # ==================== FOREIGN KEY RELATIONSHIP TESTS ====================

    def test_curriculum_reverse_relation(self):
        """Test accessing periodes from curriculum via reverse relation."""
        periodes = self.curriculum.periode.all()
        self.assertEqual(periodes.count(), 1)
        self.assertEqual(periodes.first(), self.periode)

    def test_multiple_periodes_reverse_relation(self):
        """Test reverse relation returns all periodes for a curriculum."""
        Periode.objects.create(name='Semestre 2', curriculum=self.curriculum, credits=28, rank=2)
        Periode.objects.create(name='Semestre 3', curriculum=self.curriculum, credits=20, rank=3)
        self.assertEqual(self.curriculum.periode.count(), 3)

    def test_cascade_delete_curriculum_deletes_periodes(self):
        """Test that deleting a curriculum also deletes its periodes."""
        periode_id = self.periode.id
        curriculum_id = self.curriculum.id

        self.curriculum.delete()

        self.assertFalse(Curriculum.objects.filter(id=curriculum_id).exists())
        self.assertFalse(Periode.objects.filter(id=periode_id).exists())

    def test_deleting_periode_does_not_delete_curriculum(self):
        """Test that deleting a periode does not delete its curriculum."""
        curriculum_id = self.curriculum.id
        self.periode.delete()
        self.assertTrue(Curriculum.objects.filter(id=curriculum_id).exists())

    # ==================== UPDATE TESTS ====================

    def test_update_name(self):
        """Test updating periode name."""
        self.periode.name = 'Nouveau Semestre'
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.name, 'Nouveau Semestre')

    def test_update_credits(self):
        """Test updating periode credits."""
        self.periode.credits = 20
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.credits, 20)

    def test_update_rank(self):
        """Test updating periode rank."""
        self.periode.rank = 5
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.rank, 5)

    def test_update_moyenne(self):
        """Test updating periode moyenne."""
        self.periode.moyenne = 16.75
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.moyenne, 16.75)

    def test_update_curriculum(self):
        """Test changing a periode's curriculum."""
        curriculum2 = Curriculum.objects.create(title='Curriculum Maths')
        self.periode.curriculum = curriculum2
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertEqual(self.periode.curriculum, curriculum2)

    def test_set_rank_to_null(self):
        """Test setting rank to null after being set."""
        self.periode.rank = None
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertIsNone(self.periode.rank)

    def test_set_moyenne_to_null(self):
        """Test setting moyenne to null after being set."""
        self.periode.moyenne = None
        self.periode.save()
        self.periode.refresh_from_db()
        self.assertIsNone(self.periode.moyenne)

    # ==================== DELETE TESTS ====================

    def test_delete_periode(self):
        """Test deleting a periode."""
        periode_id = self.periode.id
        self.periode.delete()
        self.assertFalse(Periode.objects.filter(id=periode_id).exists())

    # ==================== QUERY TESTS ====================

    def test_filter_by_name(self):
        """Test filtering periodes by name."""
        Periode.objects.create(name='Module B', curriculum=self.curriculum, credits=10)
        result = Periode.objects.filter(name='Module B')
        self.assertEqual(result.count(), 1)

    def test_filter_by_credits(self):
        """Test filtering periodes by credits."""
        Periode.objects.create(name='Module B', curriculum=self.curriculum, credits=10)
        result = Periode.objects.filter(credits=30)
        self.assertEqual(result.count(), 1)

    def test_filter_by_rank(self):
        """Test filtering periodes by rank."""
        Periode.objects.create(name='Semestre 2', curriculum=self.curriculum, credits=25, rank=2)
        result = Periode.objects.filter(rank=1)
        self.assertEqual(result.count(), 1)

    def test_filter_by_moyenne_range(self):
        """Test filtering periodes by moyenne range."""
        Periode.objects.create(name='Semestre 2', curriculum=self.curriculum, credits=25, moyenne=10.0)
        result = Periode.objects.filter(moyenne__gte=14.0)
        self.assertEqual(result.count(), 1)

    def test_filter_by_curriculum(self):
        """Test filtering periodes by curriculum."""
        curriculum2 = Curriculum.objects.create(title='Curriculum 2')
        Periode.objects.create(name='Other', curriculum=curriculum2, credits=15)
        result = Periode.objects.filter(curriculum=self.curriculum)
        self.assertEqual(result.count(), 1)

    def test_filter_null_rank(self):
        """Test filtering periodes where rank is null."""
        Periode.objects.create(name='No Rank', curriculum=self.curriculum, credits=10, rank=None)
        result = Periode.objects.filter(rank__isnull=True)
        self.assertEqual(result.count(), 1)

    def test_filter_null_moyenne(self):
        """Test filtering periodes where moyenne is null."""
        Periode.objects.create(name='No Moyenne', curriculum=self.curriculum, credits=10, moyenne=None)
        result = Periode.objects.filter(moyenne__isnull=True)
        self.assertGreaterEqual(result.count(), 1)

    # ==================== EDGE CASES ====================

    def test_credits_zero(self):
        """Test that credits can be zero."""
        periode = Periode.objects.create(name='Zero Credits', curriculum=self.curriculum, credits=0)
        self.assertEqual(periode.credits, 0)

    def test_credits_negative(self):
        """Test that credits can be negative (no DB constraint)."""
        periode = Periode.objects.create(name='Negative Credits', curriculum=self.curriculum, credits=-5)
        self.assertEqual(periode.credits, -5)

    def test_moyenne_zero(self):
        """Test that moyenne can be zero."""
        periode = Periode.objects.create(name='Zero Moyenne', curriculum=self.curriculum, credits=10, moyenne=0.0)
        self.assertEqual(periode.moyenne, 0.0)

    def test_moyenne_max_value(self):
        """Test that moyenne can hold a high float value."""
        periode = Periode.objects.create(name='Max Moyenne', curriculum=self.curriculum, credits=10, moyenne=20.0)
        self.assertEqual(periode.moyenne, 20.0)

    def test_name_with_special_characters(self):
        """Test name with special characters."""
        periode = Periode.objects.create(
            name='Semestre & Spécial - Avancé',
            curriculum=self.curriculum,
            credits=15,
        )
        self.assertEqual(periode.name, 'Semestre & Spécial - Avancé')

    def test_name_with_unicode(self):
        """Test name with unicode characters."""
        periode = Periode.objects.create(
            name='الفصل الأول',
            curriculum=self.curriculum,
            credits=15,
        )
        self.assertEqual(periode.name, 'الفصل الأول')

    def test_name_at_max_length(self):
        """Test name at max length of 100 characters."""
        long_name = 'A' * 100
        periode = Periode.objects.create(name=long_name, curriculum=self.curriculum, credits=10)
        self.assertEqual(len(periode.name), 100)