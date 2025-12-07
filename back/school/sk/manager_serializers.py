from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lesson, LessonBalance, Payment

User = get_user_model()


class ManagerClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "student_full_name", "parent_full_name", "role")


class ManagerLessonSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "student",
            "student_email",
            "parent_full_name",
            "teacher",
            "teacher_email",
            "link",
            "scheduled_at",
            "status",
            "comment",
            "debited_from_balance",
            "created_at",
        )


class ManagerLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока менеджером.
    Может указать student_email и teacher_email вместо ID.
    """
    student_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    teacher_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    scheduled_at = serializers.DateTimeField(required=True)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "teacher", "teacher_email", "scheduled_at", "link", "comment")

    def validate(self, attrs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Validating lesson creation with attrs: {attrs}")
        
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
        
        teacher_email = attrs.pop('teacher_email', None)
        if teacher_email:
            teacher_email = teacher_email.strip() if isinstance(teacher_email, str) else None
            if teacher_email:
                try:
                    teacher = User.objects.get(email__iexact=teacher_email)
                    attrs['teacher'] = teacher
                    logger.info(f"Found teacher: {teacher.id} - {teacher.email}")
                except User.DoesNotExist:
                    logger.warning(f"Teacher not found: {teacher_email}")
                    raise serializers.ValidationError({"teacher_email": "Teacher with this email not found"})
                except User.MultipleObjectsReturned:
                    logger.warning(f"Multiple teachers found: {teacher_email}")
                    raise serializers.ValidationError({"teacher_email": "Multiple teachers with this email found"})
        
        # Проверяем, что хотя бы один способ указания пользователя есть
        if not attrs.get('student'):
            logger.error("Student is required but not provided")
            raise serializers.ValidationError({"student": "Either student or student_email is required"})
        
        if not attrs.get('teacher'):
            logger.error("Teacher is required but not provided")
            raise serializers.ValidationError({"teacher": "Either teacher or teacher_email is required"})
        
        logger.info(f"Validation successful. Final attrs: student={attrs.get('student')}, teacher={attrs.get('teacher')}")
        return attrs


class ManagerLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Менеджер может менять время, ссылку, статус, комментарий.
    """
    class Meta:
        model = Lesson
        fields = ("scheduled_at", "status", "link", "comment")


class ManagerBalanceSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = LessonBalance
        fields = ("student", "student_email", "lessons_available", "updated_at")


class ManagerPaymentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "student", "student_email", "amount", "package_name", "paid_at", "confirmed")
