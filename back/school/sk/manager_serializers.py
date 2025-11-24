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
            "id", "student", "student_email",
            "parent_full_name", "teacher", "teacher_email",
            "link", "scheduled_at", "status", "comment",
            "debited_from_balance", "created_at"
        )

class ManagerLessonUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("scheduled_at", "link", "status", "comment", "teacher")

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
