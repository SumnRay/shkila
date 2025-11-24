from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, LessonBalance, Payment, StudentProfile

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("level", "xp", "season_currency")


class StudentDashboardSerializer(serializers.Serializer):
    """
    Объединённый ответ для /api/student/dashboard/
    """
    id = serializers.IntegerField()
    email = serializers.EmailField()
    student_full_name = serializers.CharField()
    role = serializers.CharField()
    balance = serializers.IntegerField()
    level = serializers.IntegerField()
    xp = serializers.IntegerField()
    season_currency = serializers.IntegerField()


class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title", "description", "default_lessons", "default_price")


class StudentLessonSerializer(serializers.ModelSerializer):
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "teacher", "teacher_email",
            "link",
            "scheduled_at",
            "status",
            "comment",
            "debited_from_balance",
            "created_at",
        )


class StudentBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBalance
        fields = ("lessons_available", "updated_at")


class StudentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "amount", "package_name", "paid_at", "confirmed")


class StudentPaymentCreateSerializer(serializers.Serializer):
    """
    Заявка на оплату от ученика (похож на абитуриента).
    """
    course_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    package_name = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_course_id(self, value):
        from .models import Course
        if not Course.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Курс не найден или не активен")
        return value
