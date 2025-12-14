from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Lesson, LessonBalance, AuditLog, Course, Module, LessonTopic

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
    course = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "student",
            "student_email",
            "parent_full_name",
            "teacher",
            "teacher_email",
            "course",
            "link",
            "scheduled_at",
            "status",
            "comment",
            "debited_from_balance",
            "created_at",
        )
    
    def get_course(self, obj):
        """Получение названия курса"""
        if obj.course:
            return obj.course.title
        return None


class AdminLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока админом.
    Может указать student_email и teacher_email вместо ID.
    """
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    student_email = serializers.EmailField(write_only=True, required=False)
    teacher_email = serializers.EmailField(write_only=True, required=False)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)
    is_trial = serializers.BooleanField(required=False, default=False, help_text="Пробное занятие (не списывается с баланса)")

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "teacher", "teacher_email", "course", "scheduled_at", "link", "comment", "is_trial")

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
        
        # Валидация баланса и пробных занятий (аналогично менеджеру)
        is_trial = attrs.get('is_trial', False)
        student = attrs.get('student')
        
        if student:
            from .models import LessonBalance
            student_role = getattr(student, 'role', None)
            lb, _ = LessonBalance.objects.get_or_create(student=student)
            
            if is_trial:
                # Пробные занятия можно создавать для абитуриентов или учеников с нулевым балансом
                if student_role == 'STUDENT' and lb.lessons_available > 0:
                    raise serializers.ValidationError({
                        "is_trial": "Пробные занятия можно создавать только для абитуриентов или учеников с нулевым балансом"
                    })
            else:
                # Обычные занятия можно создавать только для учеников с положительным балансом
                if student_role != 'STUDENT':
                    raise serializers.ValidationError({
                        "student": "Обычные занятия можно создавать только для учеников. Для абитуриентов создайте пробное занятие (is_trial=true)."
                    })
                if lb.lessons_available <= 0:
                    raise serializers.ValidationError({
                        "student": "Нельзя создать урок для ученика с нулевым балансом. Создайте пробное занятие (is_trial=true) или пополните баланс ученика."
                    })
        
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


# ======= COURSES, MODULES, TOPICS =======


class LessonTopicSerializer(serializers.ModelSerializer):
    """Сериализатор для темы занятия"""
    class Meta:
        model = LessonTopic
        fields = ("id", "title", "description", "order", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class LessonTopicCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления темы занятия"""
    class Meta:
        model = LessonTopic
        fields = ("title", "description", "order")


class ModuleSerializer(serializers.ModelSerializer):
    """Сериализатор для модуля с темами"""
    topics = LessonTopicSerializer(many=True, read_only=True)
    topics_count = serializers.IntegerField(source="topics.count", read_only=True)

    class Meta:
        model = Module
        fields = ("id", "title", "description", "order", "topics", "topics_count", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления модуля"""
    class Meta:
        model = Module
        fields = ("title", "description", "order")


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса с модулями"""
    modules = ModuleSerializer(many=True, read_only=True)
    modules_count = serializers.IntegerField(source="modules.count", read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "title", "modules", "modules_count", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления курса"""
    class Meta:
        model = Course
        fields = ("title",)
