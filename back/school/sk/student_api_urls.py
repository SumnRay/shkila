from django.urls import path
from .teacher_api_views import (
    TeacherLessonsListAPI,
    TeacherLessonDetailAPI,
    TeacherLessonUpdateAPI,
    TeacherStudentsListAPI,
    TeacherStudentLessonsAPI,
)

urlpatterns = [
    # Расписание / уроки
    path("lessons/", TeacherLessonsListAPI.as_view()),                   # GET список уроков
    path("lessons/<int:pk>/", TeacherLessonDetailAPI.as_view()),         # GET один урок
    path("lessons/<int:pk>/update/", TeacherLessonUpdateAPI.as_view()),  # PATCH обновление

    # Журнал учеников
    path("students/", TeacherStudentsListAPI.as_view()),                             # GET список учеников
    path("students/<int:student_id>/lessons/", TeacherStudentLessonsAPI.as_view()),  # GET журнал по ученику
]
