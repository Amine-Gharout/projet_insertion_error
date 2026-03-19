from django.test import TestCase
from django.db import IntegrityError
from curriculum.models import Curriculum
from student.models import Student
from formation.models import Formation
import uuid


class CurriculumModelTest(TestCase):
    """Tests for the Curriculum model."""

    def setUp(self):
        """Set up test data before each test."""
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

    # ==================== CREATION TESTS ====================

    def test_curriculum_creation_with_all_fields(self):
        """Test creating a curriculum with all fields."""
        self.assertEqual(self.curriculum.section, 'A')
        self.assertEqual(self.curriculum.group, 'G1')
        self.assertEqual(self.curriculum.status, 'active')
        self.assertEqual(self.curriculum.rank, 1)
        self.assertEqual(self.curriculum.moyenne_finale, 14.5)
        self.assertEqual(self.curriculum.moyenne_rachat, 12.0)
        self.assertEqual(self.curriculum.moyenne_concours, 15.0)
        self.assertEqual(self.curriculum.student, self.student)
        self.assertEqual(self.curriculum.formation, self.formation)
        self.assertIsInstance(self.curriculum.id, uuid.UUID)

    def test_curriculum_creation_without_optional_fields(self):
        """Test creating a curriculum without optional fields."""
        curriculum = Curriculum.objects.create(
            student=self.student2,
            formation=self.formation,
            status='active',
        )
        self.assertIsNone(curriculum.section)
        self.assertIsNone(curriculum.group)
        self.assertIsNone(curriculum.rank)
        self.assertIsNone(curriculum.moyenne_finale)
        self.assertIsNone(curriculum.moyenne_rachat)
        self.assertIsNone(curriculum.moyenne_concours)

    def test_curriculum_requires_status(self):
        """Test that status is required."""
        with self.assertRaises(Exception):
            Curriculum.objects.create(
                student=self.student2,
                formation=self.formation2,
            )

    # ==================== UNIQUE TOGETHER TESTS ====================

    def test_unique_together_student_formation(self):
        """Test that student + formation combination must be unique."""
        with self.assertRaises(IntegrityError):
            Curriculum.objects.create(
                student=self.student,
                formation=self.formation,
                status='active',
            )

    def test_same_student_different_formation_is_allowed(self):
        """Test that same student can have different formations."""
        curriculum2 = Curriculum.objects.create(
            student=self.student,
            formation=self.formation2,
            status='active',
        )
        self.assertEqual(curriculum2.student, self.student)
        self.assertNotEqual(curriculum2.formation, self.formation)

    def test_same_formation_different_student_is_allowed(self):
        """Test that same formation can have different students."""
        curriculum2 = Curriculum.objects.create(
            student=self.student2,
            formation=self.formation,
            status='active',
        )
        self.assertEqual(curriculum2.formation, self.formation)
        self.assertNotEqual(curriculum2.student, self.student)

    # ==================== UUID TESTS ====================

    def test_uuid_is_auto_generated(self):
        """Test that UUID is automatically generated."""
        self.assertIsNotNone(self.curriculum.id)
        self.assertIsInstance(self.curriculum.id, uuid.UUID)

    def test_uuid_is_unique(self):
        """Test that each curriculum gets a unique UUID."""
        curriculum2 = Curriculum.objects.create(
            student=self.student2,
            formation=self.formation,
            status='active',
        )
        self.assertNotEqual(self.curriculum.id, curriculum2.id)

    def test_uuid_is_not_editable(self):
        """Test that UUID field is not editable."""
        field = Curriculum._meta.get_field('id')
        self.assertFalse(field.editable)

    # ==================== TIMESTAMP TESTS ====================

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        self.assertIsNotNone(self.curriculum.created_at)

    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set."""
        self.assertIsNotNone(self.curriculum.updated_at)

    def test_created_at_does_not_change_on_save(self):
        """Test that created_at does not change on subsequent saves."""
        original = self.curriculum.created_at
        self.curriculum.status = 'graduated'
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.created_at, original)

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when the record is updated."""
        original = self.curriculum.updated_at
        self.curriculum.status = 'graduated'
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertGreaterEqual(self.curriculum.updated_at, original)

    # ==================== STRING REPRESENTATION TESTS ====================

    def test_str_representation(self):
        """Test the __str__ method."""
        expected = f'{self.student} - {self.formation} (active)'
        self.assertEqual(str(self.curriculum), expected)

    def test_str_with_different_status(self):
        """Test __str__ with different status."""
        curriculum = Curriculum.objects.create(
            student=self.student2,
            formation=self.formation,
            status='graduated',
        )
        expected = f'{self.student2} - {self.formation} (graduated)'
        self.assertEqual(str(curriculum), expected)

    # ==================== META OPTIONS TESTS ====================

    def test_meta_ordering(self):
        """Test ordering by formation then rank."""
        c2 = Curriculum.objects.create(student=self.student2, formation=self.formation, status='active', rank=2)
        curricula = list(Curriculum.objects.filter(formation=self.formation).exclude(rank=None))
        ranks = [c.rank for c in curricula]
        self.assertEqual(ranks, sorted(ranks))

    def test_meta_verbose_name(self):
        """Test verbose_name."""
        self.assertEqual(Curriculum._meta.verbose_name, 'Curriculum')

    def test_meta_verbose_name_plural(self):
        """Test verbose_name_plural."""
        self.assertEqual(Curriculum._meta.verbose_name_plural, 'Curriculums')

    def test_meta_db_table(self):
        """Test db_table."""
        self.assertEqual(Curriculum._meta.db_table, 'curriculum')

    # ==================== FIELD CONSTRAINTS TESTS ====================

    def test_section_max_length(self):
        """Test section max_length is 20."""
        field = Curriculum._meta.get_field('section')
        self.assertEqual(field.max_length, 20)

    def test_section_is_nullable(self):
        """Test section is nullable."""
        field = Curriculum._meta.get_field('section')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_group_max_length(self):
        """Test group max_length is 20."""
        field = Curriculum._meta.get_field('group')
        self.assertEqual(field.max_length, 20)

    def test_group_is_nullable(self):
        """Test group is nullable."""
        field = Curriculum._meta.get_field('group')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_status_max_length(self):
        """Test status max_length is 20."""
        field = Curriculum._meta.get_field('status')
        self.assertEqual(field.max_length, 20)

    def test_rank_is_nullable(self):
        """Test rank is nullable."""
        field = Curriculum._meta.get_field('rank')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_moyenne_finale_is_nullable(self):
        """Test moyenne_finale is nullable."""
        field = Curriculum._meta.get_field('moyenne_finale')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_moyenne_rachat_is_nullable(self):
        """Test moyenne_rachat is nullable."""
        field = Curriculum._meta.get_field('moyenne_rachat')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_moyenne_concours_is_nullable(self):
        """Test moyenne_concours is nullable."""
        field = Curriculum._meta.get_field('moyenne_concours')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_student_is_foreign_key(self):
        """Test student is a ForeignKey."""
        field = Curriculum._meta.get_field('student')
        self.assertEqual(field.get_internal_type(), 'ForeignKey')

    def test_student_related_name(self):
        """Test student related_name is curriculums."""
        field = Curriculum._meta.get_field('student')
        self.assertEqual(field.remote_field.related_name, 'curriculums')

    def test_formation_is_foreign_key(self):
        """Test formation is a ForeignKey."""
        field = Curriculum._meta.get_field('formation')
        self.assertEqual(field.get_internal_type(), 'ForeignKey')

    def test_formation_related_name(self):
        """Test formation related_name is curriculums."""
        field = Curriculum._meta.get_field('formation')
        self.assertEqual(field.remote_field.related_name, 'curriculums')

    def test_student_on_delete_cascade(self):
        """Test student ForeignKey uses CASCADE."""
        from django.db.models import CASCADE
        field = Curriculum._meta.get_field('student')
        self.assertEqual(field.remote_field.on_delete, CASCADE)

    def test_formation_on_delete_cascade(self):
        """Test formation ForeignKey uses CASCADE."""
        from django.db.models import CASCADE
        field = Curriculum._meta.get_field('formation')
        self.assertEqual(field.remote_field.on_delete, CASCADE)

    # ==================== FOREIGN KEY RELATIONSHIP TESTS ====================

    def test_student_reverse_relation(self):
        """Test accessing curriculums from student."""
        curricula = self.student.curriculums.all()
        self.assertEqual(curricula.count(), 1)
        self.assertEqual(curricula.first(), self.curriculum)

    def test_formation_reverse_relation(self):
        """Test accessing curriculums from formation."""
        curricula = self.formation.curriculums.all()
        self.assertEqual(curricula.count(), 1)

    def test_cascade_delete_student_deletes_curriculum(self):
        """Test that deleting student deletes its curriculums."""
        curriculum_id = self.curriculum.id
        self.student.delete()
        self.assertFalse(Curriculum.objects.filter(id=curriculum_id).exists())

    def test_cascade_delete_formation_deletes_curriculum(self):
        """Test that deleting formation deletes its curriculums."""
        curriculum_id = self.curriculum.id
        self.formation.delete()
        self.assertFalse(Curriculum.objects.filter(id=curriculum_id).exists())

    def test_deleting_curriculum_does_not_delete_student(self):
        """Test deleting curriculum does not delete student."""
        student_id = self.student.id
        self.curriculum.delete()
        self.assertTrue(Student.objects.filter(id=student_id).exists())

    def test_deleting_curriculum_does_not_delete_formation(self):
        """Test deleting curriculum does not delete formation."""
        formation_id = self.formation.id
        self.curriculum.delete()
        self.assertTrue(Formation.objects.filter(id=formation_id).exists())

    # ==================== UPDATE TESTS ====================

    def test_update_status(self):
        """Test updating status."""
        self.curriculum.status = 'graduated'
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.status, 'graduated')

    def test_update_section(self):
        """Test updating section."""
        self.curriculum.section = 'B'
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.section, 'B')

    def test_update_group(self):
        """Test updating group."""
        self.curriculum.group = 'G2'
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.group, 'G2')

    def test_update_rank(self):
        """Test updating rank."""
        self.curriculum.rank = 5
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.rank, 5)

    def test_update_moyenne_finale(self):
        """Test updating moyenne_finale."""
        self.curriculum.moyenne_finale = 16.0
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertEqual(self.curriculum.moyenne_finale, 16.0)

    def test_set_section_to_null(self):
        """Test setting section to null."""
        self.curriculum.section = None
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertIsNone(self.curriculum.section)

    def test_set_rank_to_null(self):
        """Test setting rank to null."""
        self.curriculum.rank = None
        self.curriculum.save()
        self.curriculum.refresh_from_db()
        self.assertIsNone(self.curriculum.rank)

    # ==================== DELETE TESTS ====================

    def test_delete_curriculum(self):
        """Test deleting a curriculum."""
        curriculum_id = self.curriculum.id
        self.curriculum.delete()
        self.assertFalse(Curriculum.objects.filter(id=curriculum_id).exists())

    # ==================== QUERY TESTS ====================

    def test_filter_by_status(self):
        """Test filtering by status."""
        Curriculum.objects.create(student=self.student2, formation=self.formation, status='graduated')
        result = Curriculum.objects.filter(status='active')
        self.assertEqual(result.count(), 1)

    def test_filter_by_section(self):
        """Test filtering by section."""
        result = Curriculum.objects.filter(section='A')
        self.assertEqual(result.count(), 1)

    def test_filter_by_formation(self):
        """Test filtering by formation."""
        result = Curriculum.objects.filter(formation=self.formation)
        self.assertEqual(result.count(), 1)

    def test_filter_by_student(self):
        """Test filtering by student."""
        result = Curriculum.objects.filter(student=self.student)
        self.assertEqual(result.count(), 1)

    def test_filter_by_moyenne_finale_range(self):
        """Test filtering by moyenne_finale range."""
        Curriculum.objects.create(student=self.student2, formation=self.formation, status='active', moyenne_finale=10.0)
        result = Curriculum.objects.filter(moyenne_finale__gte=14.0)
        self.assertEqual(result.count(), 1)

    def test_filter_null_rank(self):
        """Test filtering where rank is null."""
        Curriculum.objects.create(student=self.student2, formation=self.formation, status='active', rank=None)
        result = Curriculum.objects.filter(rank__isnull=True)
        self.assertGreaterEqual(result.count(), 1)

    # ==================== EDGE CASES ====================

    def test_moyenne_zero(self):
        """Test that moyenne fields can be zero."""
        curriculum = Curriculum.objects.create(
            student=self.student2, formation=self.formation2,
            status='active', moyenne_finale=0.0, moyenne_rachat=0.0, moyenne_concours=0.0,
        )
        self.assertEqual(curriculum.moyenne_finale, 0.0)

    def test_rank_zero(self):
        """Test that rank can be zero."""
        curriculum = Curriculum.objects.create(
            student=self.student2, formation=self.formation, status='active', rank=0,
        )
        self.assertEqual(curriculum.rank, 0)

    def test_section_with_special_characters(self):
        """Test section with special characters."""
        curriculum = Curriculum.objects.create(
            student=self.student2, formation=self.formation, status='active', section='A-1',
        )
        self.assertEqual(curriculum.section, 'A-1')