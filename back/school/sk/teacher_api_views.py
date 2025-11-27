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

    Параметр сортировки:
      - ?ordering=scheduled_at или -scheduled_at
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "student"]
    search_fields = [
        "student__email",
        "student__student_full_name",
        "parent_full_name",
    ]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["-scheduled_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher").all()
        # если не админ и не суперюзер — показываем только свои уроки
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs


class TeacherLessonDetailAPI(generics.RetrieveAPIView):
    """
    Детальная карточка урока (доступна только своему учителю и админам).
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher").all()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs


class TeacherLessonUpdateAPI(generics.UpdateAPIView):
    """
    Частичное обновление урока учителем:
    - статус (PLANNED / DONE / CANCELLED)
    - комментарий
    - при необходимости ссылка

    PATCH /api/teacher/lessons/<id>/update/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonUpdateSerializer
    http_method_names = ["patch", "options", "head"]

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher").all()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs

    def perform_update(self, serializer):
        lesson = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="TEACHER_UPDATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "status": lesson.status,
            },
        )


# ======= ЖУРНАЛ УЧЕНИКОВ =======


class TeacherStudentsListAPI(generics.ListAPIView):
    """
    Список учеников, у которых есть уроки с данным преподавателем.

    Поиск:
      - ?search=строка  (по email / ФИО ученика / ФИО родителя)
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherStudentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "student_full_name", "parent_full_name"]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.filter(lessons_as_student__isnull=False).distinct()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(lessons_as_student__teacher=user).distinct()
        return qs


class TeacherStudentLessonsAPI(generics.ListAPIView):
    """
    Журнал по конкретному ученику (все его занятия).
    Доступен только его учителю и админам.

    GET /api/teacher/students/<student_id>/lessons/
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
        qs = Lesson.objects.select_related("student", "teacher").filter(
            student_id=student_id
        )
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs
