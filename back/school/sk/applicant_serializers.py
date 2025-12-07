from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, LessonBalance, Payment, Module, LessonTopic

User = get_user_model()


class PublicLessonTopicSerializer(serializers.ModelSerializer):
    """Публичный сериализатор для темы занятия"""
    class Meta:
        model = LessonTopic
        fields = ("id", "title", "description", "order")


class PublicModuleSerializer(serializers.ModelSerializer):
    """Публичный сериализатор для модуля с темами"""
    topics = PublicLessonTopicSerializer(many=True, read_only=True)
    topics_count = serializers.IntegerField(source="topics.count", read_only=True)

    class Meta:
        model = Module
        fields = ("id", "title", "description", "order", "topics", "topics_count")


class ApplicantCourseSerializer(serializers.ModelSerializer):
    """Публичный сериализатор для курса с модулями и темами"""
    modules = PublicModuleSerializer(many=True, read_only=True)
    modules_count = serializers.IntegerField(source="modules.count", read_only=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "default_lessons", "default_price", "modules", "modules_count")


class ApplicantBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBalance
        fields = ("lessons_available", "updated_at")


class ApplicantPaymentCreateSerializer(serializers.Serializer):
    """
    То, что абитуриент отправляет при "оплате":
    - id курса
    - сумма
    - название пакета (опционально)
    """
    course_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    package_name = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_course_id(self, value):
        from .models import Course
        if not Course.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Курс не найден или не активен")
        return value


class ApplicantPaymentSerializer(serializers.ModelSerializer):
    """
    Просмотр истории оплат самим абитуриентом.
    """
    class Meta:
        model = Payment
        fields = ("id", "amount", "package_name", "paid_at", "confirmed")
