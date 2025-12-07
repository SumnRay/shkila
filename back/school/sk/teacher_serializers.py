from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lesson

User = get_user_model()


class TeacherLessonSerializer(serializers.ModelSerializer):
    """
    Карточка урока для учителя (просмотр).
    """
    student_email = serializers.EmailField(source="student.email", read_only=True)
    student_name = serializers.CharField(source="student.student_full_name", read_only=True)
    parent_full_name = serializers.CharField(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "student", "student_email", "student_name",
            "parent_full_name",
            "teacher", "teacher_email",
            "link",
            "scheduled_at",
            "status",
            "comment",
            "debited_from_balance",
            "created_at",
        )


class TeacherLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Что учитель может менять в карточке урока:
    - статус (PLANNED/DONE/CANCELLED)
    - комментарий/отметку
    - при необходимости ссылку (если по договорённости)
    """
    class Meta:
        model = Lesson
        fields = ("status", "comment", "link")


class TeacherLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока учителем.
    Учитель может указать student_email вместо ID.
    Учитель автоматически назначается как teacher.
    """
    student_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)
    scheduled_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "scheduled_at", "link", "comment")

    def validate(self, attrs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Validating teacher lesson creation with attrs: {attrs}")
        
        # Если передан email, находим пользователя по email
        student_email = attrs.pop('student_email', None)
        if student_email:
            student_email = student_email.strip() if isinstance(student_email, str) else None
            if student_email:
                try:
                    student = User.objects.get(email__iexact=student_email)
                    attrs['student'] = student
                    logger.info(f"Found student: {student.id} - {student.email}")
                except User.DoesNotExist:
                    logger.warning(f"Student not found: {student_email}")
                    raise serializers.ValidationError({"student_email": "Student with this email not found"})
                except User.MultipleObjectsReturned:
                    logger.warning(f"Multiple students found: {student_email}")
                    raise serializers.ValidationError({"student_email": "Multiple students with this email found"})
        
        # Проверяем, что хотя бы один способ указания ученика есть
        if not attrs.get('student'):
            logger.error("Student is required but not provided")
            raise serializers.ValidationError({"student": "Either student or student_email is required"})
        
        logger.info(f"Validation successful. Final attrs: student={attrs.get('student')}")
        return attrs


class TeacherStudentSerializer(serializers.ModelSerializer):
    """
    Список учеников учителя (для журнала).
    """
    class Meta:
        model = User
        fields = ("id", "email", "student_full_name", "parent_full_name")
