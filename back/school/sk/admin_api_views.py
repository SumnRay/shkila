from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdminRole
from .models import Payment, Lesson, LessonBalance, AuditLog
from .admin_serializers import (
    AdminUserListSerializer, AdminSetRoleSerializer,
    PaymentSerializer, LessonSerializer, LessonBalanceSerializer, AuditLogSerializer
)

User = get_user_model()


# ======= USERS =======

class AdminUserListAPI(generics.ListAPIView):
    """
    Список всех пользователей (поиск/фильтры):
    ?role=STUDENT|TEACHER|... & search=часть_email_или_ФИО
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = AdminUserListSerializer
    queryset = User.objects.all().order_by('-date_joined')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role", "is_superuser"]
    search_fields = ["email", "student_full_name", "parent_full_name"]
    ordering_fields = ["id", "email", "date_joined"]


class AdminSetRoleAPI(APIView):
    """
    Назначение роли пользователю: PATCH /api/admin/users/{id}/set-role/
    body: {"role": "TEACHER"}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)

        ser = AdminSetRoleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new_role = ser.validated_data["role"]

        user.role = new_role
        # базовая синхронизация staff-флагов (по желанию):
        if new_role == "ADMIN":
            user.is_staff = True
        user.save()

        AuditLog.objects.create(
            actor=request.user,
            action="SET_ROLE",
            meta={"user_id": user.id, "email": user.email, "new_role": new_role},
        )
        return Response(AdminUserListSerializer(user).data)
        

# ======= PAYMENTS / BALANCE =======

class AdminPaymentListAPI(generics.ListCreateAPIView):
    """
    GET: список платежей (фильтры: confirmed, student)
    POST: создать запись оплаты (обычно создаёт менеджер, но админ может всё)
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Payment.objects.select_related("student").all().order_by('-paid_at')
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["confirmed", "student"]
    ordering_fields = ["paid_at", "amount", "id"]

class AdminPaymentConfirmAPI(APIView):
    """
    Подтвердить оплату и начислить N занятий на баланс (через ЛК админа).
    + Если студент был абитуриентом (APPLICANT), меняем роль на STUDENT.
    POST /api/admin/payments/{id}/confirm/
    Body: {"lessons_to_add": 4}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

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

        # подтверждаем оплату
        p.confirmed = True
        p.save()

        # начисляем занятия на баланс
        bal, _ = LessonBalance.objects.get_or_create(student=p.student)
        bal.lessons_available += lessons_to_add
        bal.save()

        # 🔹 промоушен: APPLICANT → STUDENT
        student = p.student
        old_role = getattr(student, "role", None)
        if old_role == "APPLICANT":
            student.role = "STUDENT"
            student.save(update_fields=["role"])

        AuditLog.objects.create(
            actor=request.user,
            action="ADMIN_CONFIRM_PAYMENT",
            meta={
                "payment_id": p.id,
                "student_id": student.id,
                "lessons_added": lessons_to_add,
                "old_role": old_role,
                "new_role": student.role,
            },
        )
        return Response({"detail": "ok"})

class AdminBalanceGetAPI(generics.RetrieveAPIView):
    """
    Баланс ученика: GET /api/admin/students/{id}/balance/
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = LessonBalanceSerializer
    lookup_url_kwarg = "student_id"

    def get_object(self):
        from .models import LessonBalance
        student_id = self.kwargs["student_id"]
        bal, _ = LessonBalance.objects.get_or_create(student_id=student_id)
        return bal


# ======= LESSONS =======

class AdminLessonListAPI(generics.ListCreateAPIView):
    """
    GET: список уроков (фильтры: student, teacher, status)
    POST: создать урок (админ может создать как менеджер/учитель)
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = LessonSerializer
    queryset = Lesson.objects.select_related("student","teacher").all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["student", "teacher", "status"]
    ordering_fields = ["scheduled_at", "created_at", "id"]

class AdminLessonDebitAPI(APIView):
    """
    Проставить списание занятия с баланса и/или отметить как проведён.
    POST /api/admin/lessons/{id}/debit/
    body: {"mark_done": true}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

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
            action="DEBIT_LESSON",
            meta={"lesson_id": les.id, "student": les.student_id, "mark_done": mark_done},
        )
        return Response({"detail": "ok"})


# ======= AUDIT LOG =======

class AdminAuditLogListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related("actor").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "actor__email"]
    ordering_fields = ["created_at", "id"]
    ordering = ["-created_at"]
