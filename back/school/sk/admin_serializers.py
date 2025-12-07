from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Lesson, LessonBalance, AuditLog

User = get_user_model()


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "student_full_name",
            "parent_full_name",
            "role",
            "is_staff",
            "is_superuser",
        )


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Детальный просмотр/редактирование пользователя в админке.
    Роль тут только для отображения — менять её отдельным эндпоинтом.
    """
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "student_full_name",
            "parent_full_name",
            "role",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = ("id", "role", "is_staff", "is_superuser")


class AdminSetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[
            ("ADMIN", "ADMIN"),
            ("MANAGER", "MANAGER"),
            ("TEACHER", "TEACHER"),
            ("STUDENT", "STUDENT"),
            ("APPLICANT", "APPLICANT"),
        ]
    )


class PaymentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "student",
            "student_email",
            "amount",
            "package_name",
            "paid_at",
            "confirmed",
        )


class LessonBalanceSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = LessonBalance
        fields = ("student", "student_email", "lessons_available", "updated_at")


class LessonSerializer(serializers.ModelSerializer):
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


class AdminLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока админом.
    Может указать student_email и teacher_email вместо ID.
    """
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    student_email = serializers.EmailField(write_only=True, required=False)
    teacher_email = serializers.EmailField(write_only=True, required=False)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "teacher", "teacher_email", "scheduled_at", "link", "comment")

    def validate(self, attrs):
        # Если передан email, находим пользователя по email
        if attrs.get('student_email'):
            student_email = attrs.pop('student_email', '').strip()
            if student_email:
                try:
                    student = User.objects.get(email__iexact=student_email)
                    attrs['student'] = student
                except User.DoesNotExist:
                    raise serializers.ValidationError({"student_email": "Student with this email not found"})
                except User.MultipleObjectsReturned:
                    raise serializers.ValidationError({"student_email": "Multiple students with this email found"})
        
        if attrs.get('teacher_email'):
            teacher_email = attrs.pop('teacher_email', '').strip()
            if teacher_email:
                try:
                    teacher = User.objects.get(email__iexact=teacher_email)
                    attrs['teacher'] = teacher
                except User.DoesNotExist:
                    raise serializers.ValidationError({"teacher_email": "Teacher with this email not found"})
                except User.MultipleObjectsReturned:
                    raise serializers.ValidationError({"teacher_email": "Multiple teachers with this email found"})
        
        # Проверяем, что хотя бы один способ указания пользователя есть
        if not attrs.get('student'):
            raise serializers.ValidationError({"student": "Either student or student_email is required"})
        
        if not attrs.get('teacher'):
            raise serializers.ValidationError({"teacher": "Either teacher or teacher_email is required"})
        
        return attrs


class AdminLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Обновление урока админом.
    Может менять время, ссылку, статус, комментарий.
    """
    class Meta:
        model = Lesson
        fields = ("scheduled_at", "status", "link", "comment")


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "actor", "actor_email", "action", "meta", "created_at")
