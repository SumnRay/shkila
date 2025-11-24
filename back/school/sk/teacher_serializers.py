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


class TeacherStudentSerializer(serializers.ModelSerializer):
    """
    Список учеников учителя (для журнала).
    """
    class Meta:
        model = User
        fields = ("id", "email", "student_full_name", "parent_full_name")
