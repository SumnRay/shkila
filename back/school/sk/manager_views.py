from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsManagerOrAdmin
from .models import Lesson, LessonBalance, Payment, AuditLog
from .manager_serializers import (
    ManagerClientSerializer, ManagerLessonSerializer, ManagerLessonUpdateSerializer,
    ManagerBalanceSerializer, ManagerPaymentSerializer
)

User = get_user_model()

# ======= CLIENTS =======

class ManagerClientsListAPI(generics.ListAPIView):
    """
    Список клиентов (обычно STUDENT и APPLICANT), с поиском/фильтрами.
    ?role=STUDENT|APPLICANT & search=email_or_name
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerClientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role"]
    search_fields = ["email", "student_full_name", "parent_full_name"]
    ordering_fields = ["id", "email"]
    queryset = User.objects.all().order_by("-id")


# ======= SCHEDULE / LESSONS =======

class ManagerLessonsListCreateAPI(generics.ListCreateAPIView):
    """
    Расписание/список уроков (GET) + назначить урок (POST).
    Фильтры: student, teacher, status; сортировки: scheduled_at, created_at.
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["student", "teacher", "status"]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    queryset = Lesson.objects.select_related("student", "teacher").all().order_by("-created_at")

class ManagerLessonUpdateAPI(generics.UpdateAPIView):
    """
    Перенести/обновить урок (время, ссылка, статус, назначить учителя).
    PATCH /api/manager/lessons/{id}/
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerLessonUpdateSerializer
    queryset = Lesson.objects.all()

    def perform_update(self, serializer):
        obj = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="MANAGER_UPDATE_LESSON",
            meta={"lesson_id": obj.id}
        )

class ManagerLessonCancelAPI(APIView):
    """
    Отменить урок.
    POST /api/manager/lessons/{id}/cancel/
    """
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, pk):
        try:
            les = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "lesson not found"}, status=404)
        les.status = "CANCELLED"
        les.save()
        AuditLog.objects.create(
            actor=request.user,
            action="MANAGER_CANCEL_LESSON",
            meta={"lesson_id": les.id}
        )
        return Response({"detail": "ok"})


class ManagerLessonDebitAPI(APIView):
    """
    Списать одно занятие по уроку (и опционально отметить как проведён).
    POST /api/manager/lessons/{id}/debit/
    Body: {"mark_done": true}
    """
    permission_classes = [IsManagerOrAdmin]

    @transaction.atomic
    def post(self, request, pk):
        mark_done = bool(request.data.get("mark_done", False))
        try:
            les = Lesson.objects.select_for_update().get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "lesson not found"}, status=404)

        if not les.debited_from_balance:
            bal, _ = LessonBalance.objects.get_or_create(student=les.student)
            if bal.lessons_available <= 0:
                return Response({"detail": "no lessons available"}, status=400)
            bal.lessons_available -= 1
            bal.save()
            les.debited_from_balance = True

        if mark_done:
            les.status = "DONE"
        les.save()

        AuditLog.objects.create(
            actor=request.user,
            action="MANAGER_DEBIT_LESSON",
            meta={"lesson_id": les.id, "mark_done": mark_done}
        )
        return Response({"detail": "ok"})


# ======= PAYMENTS / BALANCE =======

class ManagerPaymentsListCreateAPI(generics.ListCreateAPIView):
    """
    Список оплат (GET) и создание записи оплаты (POST).
    Фильтры: confirmed, student.
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["confirmed", "student"]
    ordering_fields = ["paid_at", "amount", "id"]
    queryset = Payment.objects.select_related("student").all().order_by("-paid_at")

class ManagerPaymentConfirmAPI(APIView):
    """
    Подтвердить оплату и начислить N занятий на баланс.
    POST /api/manager/payments/{id}/confirm/
    Body: {"lessons_to_add": 4}
    """
    permission_classes = [IsManagerOrAdmin]

    @transaction.atomic
    def post(self, request, pk):
        lessons_to_add = int(request.data.get("lessons_to_add", 0))
        if lessons_to_add <= 0:
            return Response({"detail": "lessons_to_add must be > 0"}, status=400)
        try:
            p = Payment.objects.select_for_update().get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"detail": "payment not found"}, status=404)

        if p.confirmed:
            return Response({"detail": "already confirmed"}, status=400)

        p.confirmed = True
        p.save()

        bal, _ = LessonBalance.objects.get_or_create(student=p.student)
        bal.lessons_available += lessons_to_add
        bal.save()

        AuditLog.objects.create(
            actor=request.user,
            action="MANAGER_CONFIRM_PAYMENT",
            meta={"payment_id": p.id, "student": p.student_id, "lessons_added": lessons_to_add}
        )
        return Response({"detail": "ok"})

class ManagerStudentBalanceAPI(generics.RetrieveAPIView):
    """
    Получить баланс ученика.
    GET /api/manager/students/{id}/balance/
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerBalanceSerializer
    lookup_url_kwarg = "student_id"

    def get_object(self):
        student_id = self.kwargs["student_id"]
        bal, _ = LessonBalance.objects.get_or_create(student_id=student_id)
        return bal
