from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Lesson, LessonBalance, AuditLog

User = get_user_model()

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "student_full_name", "parent_full_name", "role", "is_staff", "is_superuser")


class AdminSetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[
        ("ADMIN","ADMIN"), ("MANAGER","MANAGER"), ("TEACHER","TEACHER"), ("STUDENT","STUDENT"), ("APPLICANT","APPLICANT"),
    ])


class PaymentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "student", "student_email", "amount", "package_name", "paid_at", "confirmed")


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
            "id", "student", "student_email", "parent_full_name",
            "teacher", "teacher_email", "link",
            "scheduled_at", "status", "comment", "debited_from_balance", "created_at"
        )


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "actor", "actor_email", "action", "meta", "created_at")
