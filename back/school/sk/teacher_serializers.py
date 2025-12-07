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
    
    # Используем SerializerMethodField для полей, которые могут отсутствовать в БД
    cancellation_reason = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

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
            "cancellation_reason",
            "feedback",
            "debited_from_balance",
            "is_trial",
            "created_at",
        )
    
    def get_cancellation_reason(self, obj):
        """Безопасное получение причины отмены"""
        return getattr(obj, 'cancellation_reason', '')
    
    def get_feedback(self, obj):
        """Безопасное получение обратной связи"""
        return getattr(obj, 'feedback', '')


class TeacherLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Что учитель может менять в карточке урока:
    - статус (PLANNED/DONE/CANCELLED)
    - комментарий/отметку (синхронизируется для всех уроков с этим учеником)
    - причину отмены (обязательна при статусе CANCELLED)
    - обратную связь (обязательна при статусе DONE)
    - при необходимости ссылку (если по договорённости)
    """
    class Meta:
        model = Lesson
        fields = ("status", "comment", "link", "cancellation_reason", "feedback")

    def save(self, **kwargs):
        # Миграция применена, поля должны быть в БД
        # Просто сохраняем как обычно
        return super().save(**kwargs)

    def validate(self, attrs):
        # Получаем текущий статус (новый или существующий)
        new_status = attrs.get('status')
        old_status = self.instance.status if self.instance else None
        
        # Определяем финальный статус
        final_status = new_status if new_status is not None else old_status
        
        # Проверяем, меняется ли статус
        status_changed = new_status is not None and new_status != old_status
        
        # Если статус не меняется, не требуем заполнения полей
        if not status_changed:
            return attrs
        
        # Получаем причину отмены (новую или существующую) - безопасно через getattr
        cancellation_reason = attrs.get('cancellation_reason')
        if cancellation_reason is None or cancellation_reason == '':
            if self.instance:
                cancellation_reason = getattr(self.instance, 'cancellation_reason', '') or ''
            else:
                cancellation_reason = ''
        
        # Получаем обратную связь (новую или существующую) - безопасно через getattr
        feedback = attrs.get('feedback')
        if feedback is None or feedback == '':
            if self.instance:
                feedback = getattr(self.instance, 'feedback', '') or ''
            else:
                feedback = ''
        
        # Если статус меняется на CANCELLED, нужна причина отмены
        if final_status == Lesson.STATUS_CANCELLED:
            if not cancellation_reason or not cancellation_reason.strip():
                raise serializers.ValidationError({
                    "cancellation_reason": "Причина отмены обязательна при отмене занятия"
                })
        
        # Если статус меняется на DONE, нужна обратная связь
        if final_status == Lesson.STATUS_DONE:
            if not feedback or not feedback.strip():
                raise serializers.ValidationError({
                    "feedback": "Обратная связь обязательна при завершении занятия"
                })
        
        return attrs


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
