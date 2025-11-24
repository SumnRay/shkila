from django.contrib.auth import get_user_model
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsTeacherOrAdmin
from .models import Lesson, AuditLog
from .teacher_serializers import (
    TeacherLessonSerializer,
    TeacherLessonUpdateSerializer,
    TeacherStudentSerializer,
)

User = get_user_model()


# ======= УРОКИ / РАСПИСАНИЕ =======

class TeacherLessonsListAPI(generics.ListAPIView):
    """
    Список всех уроков учителя (и будущие, и прошедшие).
    Фильтры:
      - status=PLANNED|DONE|CANCELLED
      - student=<id>
      - ?ordering=scheduled_at или -scheduled_at
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "student"]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["scheduled_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher")
        # учитель видит только свои уроки, админ может всё
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs


class TeacherLessonDetailAPI(generics.RetrieveAPIView):
    """
    Детальный просмотр одной карточки урока учителем.
    GET /api/teacher/lessons/{id}/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher")
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs


class TeacherLessonUpdateAPI(generics.UpdateAPIView):
    """
    Обновление карточки урока учителем:
      - статус (PLANNED/DONE/CANCELLED)
      - комментарий
      - ссылка
    PATCH /api/teacher/lessons/{id}/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.all()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs

    def perform_update(self, serializer):
        obj = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="TEACHER_UPDATE_LESSON",
            meta={"lesson_id": obj.id},
        )


# ======= ЖУРНАЛ УЧЕНИКОВ =======

class TeacherStudentsListAPI(generics.ListAPIView):
    """
    Список всех учеников, у которых есть уроки с этим учителем.
    GET /api/teacher/students/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherStudentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "student_full_name", "parent_full_name"]
    ordering_fields = ["id", "student_full_name"]
    ordering = ["student_full_name"]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.filter(lessons_as_student__teacher=user).distinct()
        # админ может видеть всех учеников — при желании можно расширить,
        # но для строгого ЛК учителя оставляем фильтр по teacher=user
        if user.is_superuser or getattr(user, "role", None) == "ADMIN":
            qs = User.objects.filter(lessons_as_student__isnull=False).distinct()
        return qs


class TeacherStudentLessonsAPI(generics.ListAPIView):
    """
    Журнал по конкретному ученику (только уроки этого учителя).
    GET /api/teacher/students/{student_id}/lessons/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["-scheduled_at"]

    def get_queryset(self):
        user = self.request.user
        student_id = self.kwargs["student_id"]
        qs = Lesson.objects.select_related("student", "teacher").filter(student_id=student_id)
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs
