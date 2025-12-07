from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsManagerOrAdmin
from .models import Lesson, LessonBalance, Payment, AuditLog
from .manager_serializers import (
    ManagerClientSerializer,
    ManagerLessonSerializer,
    ManagerLessonCreateSerializer,
    ManagerLessonUpdateSerializer,
    ManagerBalanceSerializer,
    ManagerPaymentSerializer,
)

User = get_user_model()


# ======= КЛИЕНТЫ =======


class ManagerClientsListAPI(generics.ListAPIView):
    """
    Список клиентов (учеников/абитуриентов).
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerClientSerializer
    queryset = User.objects.all().order_by("-date_joined")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role"]
    search_fields = ["email", "student_full_name", "parent_full_name"]
    ordering_fields = ["id", "email", "date_joined"]


class ManagerUserByEmailAPI(APIView):
    """
    Поиск пользователя по email для создания урока.
    GET /api/manager/users/by-email/?email=user@example.com
    """
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        email = request.query_params.get('email', '').strip().lower()
        if not email:
            return Response({"detail": "email parameter required"}, status=400)
        
        try:
            user = User.objects.get(email__iexact=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "student_full_name": user.student_full_name,
                "parent_full_name": user.parent_full_name,
                "role": user.role,
            })
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)
        except User.MultipleObjectsReturned:
            return Response({"detail": "multiple users found"}, status=400)


# ======= УРОКИ / РАСПИСАНИЕ =======


class ManagerLessonsListCreateAPI(generics.ListCreateAPIView):
    """
    GET: список уроков (фильтры: status, student, teacher)
    POST: создать урок (назначить занятие)
    Может использовать student_email и teacher_email вместо ID.
    """
    permission_classes = [IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "student", "teacher"]
    ordering_fields = ["scheduled_at", "created_at", "id"]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ManagerLessonCreateSerializer
        return ManagerLessonSerializer

    def get_queryset(self):
        return Lesson.objects.select_related("student", "teacher").all().order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating lesson with data: {serializer.validated_data}")
        
        lesson = serializer.save()
        # Автоматически заполняем parent_full_name из профиля ученика, если не указано
        if not lesson.parent_full_name and lesson.student:
            lesson.parent_full_name = lesson.student.parent_full_name or ''
            lesson.save(update_fields=['parent_full_name'])
        AuditLog.objects.create(
            actor=self.request.user,
            action="MANAGER_CREATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "student_email": lesson.student.email,
                "teacher": lesson.teacher_id,
                "teacher_email": lesson.teacher.email if lesson.teacher else None,
                "scheduled_at": lesson.scheduled_at.isoformat(),
            },
        )


class ManagerLessonUpdateAPI(generics.UpdateAPIView):
    """
    Частичное обновление урока:
    PATCH /api/manager/lessons/{id}/
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerLessonUpdateSerializer
    queryset = Lesson.objects.select_related("student", "teacher").all()
    http_method_names = ["patch", "options", "head"]

    def perform_update(self, serializer):
        lesson = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="MANAGER_UPDATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "teacher": lesson.teacher_id,
                "status": lesson.status,
            },
        )


class ManagerLessonCancelAPI(APIView):
    """
    Отмена урока менеджером:
    POST /api/manager/lessons/{id}/cancel/
    """
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, pk):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "lesson not found"}, status=404)

        if lesson.status == Lesson.STATUS_CANCELLED:
            return Response({"detail": "already cancelled"}, status=400)

        lesson.status = Lesson.STATUS_CANCELLED
        lesson.save()

        AuditLog.objects.create(
            actor=request.user,
            action="MANAGER_CANCEL_LESSON",
            meta={"lesson_id": lesson.id, "student": lesson.student_id},
        )

        return Response({"detail": "ok"})


class ManagerLessonDebitAPI(APIView):
    """
    Списание занятия с баланса (менеджер):

    POST /api/manager/lessons/{id}/debit/
    body: {"mark_done": true/false}
    """
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, pk):
        mark_done = bool(request.data.get("mark_done", True))
        try:
            les = Lesson.objects.select_related("student").get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "lesson not found"}, status=404)

        if les.debited_from_balance:
            return Response({"detail": "already debited"}, status=400)

        with transaction.atomic():
            lb, _ = LessonBalance.objects.select_for_update().get_or_create(
                student=les.student
            )
            if lb.lessons_available <= 0:
                return Response({"detail": "no lessons available"}, status=400)

            lb.lessons_available -= 1
            lb.save()

            les.debited_from_balance = True
            if mark_done:
                les.status = Lesson.STATUS_DONE
            les.save()

            AuditLog.objects.create(
                actor=request.user,
                action="MANAGER_DEBIT_LESSON",
                meta={
                    "lesson_id": les.id,
                    "student": les.student_id,
                    "mark_done": mark_done,
                },
            )

        return Response({"detail": "ok"})


# ======= ПЛАТЕЖИ / БАЛАНС =======


class ManagerPaymentsListCreateAPI(generics.ListCreateAPIView):
    """
    GET: список платежей
    POST: создать оплату (без подтверждения)
    """
    permission_classes = [IsManagerOrAdmin]
    serializer_class = ManagerPaymentSerializer
    queryset = Payment.objects.select_related("student").all().order_by("-paid_at")
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["confirmed", "student"]
    ordering_fields = ["paid_at", "amount", "id"]


class ManagerPaymentConfirmAPI(APIView):
    """
    Подтверждение оплаты менеджером + начисление занятий:
    POST /api/manager/payments/{id}/confirm/
    body: {"lessons_to_add": 4}
    """
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, pk):
        try:
            payment = Payment.objects.select_related("student").get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"detail": "payment not found"}, status=404)

        if payment.confirmed:
            return Response({"detail": "already confirmed"}, status=400)

        lessons_to_add = int(request.data.get("lessons_to_add", 0))
        if lessons_to_add <= 0:
            return Response({"detail": "lessons_to_add must be > 0"}, status=400)

        with transaction.atomic():
            lb, _ = LessonBalance.objects.select_for_update().get_or_create(
                student=payment.student
            )
            lb.lessons_available += lessons_to_add
            lb.save()

            # Автоматически меняем роль с APPLICANT на STUDENT при первом начислении баланса
            role_changed = False
            old_role = payment.student.role
            if payment.student.role == User.Roles.APPLICANT:
                payment.student.role = User.Roles.STUDENT
                payment.student.save(update_fields=['role'])
                role_changed = True

            payment.confirmed = True
            payment.save()

            AuditLog.objects.create(
                actor=request.user,
                action="MANAGER_CONFIRM_PAYMENT",
                meta={
                    "payment_id": payment.id,
                    "student": payment.student_id,
                    "lessons_added": lessons_to_add,
                    "old_role": old_role,
                    "new_role": payment.student.role,
                    "role_changed": role_changed,
                },
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


class ManagerStudentBalanceUpdateAPI(APIView):
    """
    Изменить баланс ученика напрямую.
    PATCH /api/manager/students/{id}/balance/
    body: {"lessons_available": 10} или {"delta": 5} для изменения на +5
    """
    permission_classes = [IsManagerOrAdmin]

    def patch(self, request, student_id):
        try:
            student = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            return Response({"detail": "student not found"}, status=404)

        lessons_available = request.data.get("lessons_available")
        delta = request.data.get("delta")

        if lessons_available is None and delta is None:
            return Response({"detail": "lessons_available or delta required"}, status=400)

        with transaction.atomic():
            lb, _ = LessonBalance.objects.select_for_update().get_or_create(
                student=student
            )
            
            old_balance = lb.lessons_available
            old_role = student.role
            
            if lessons_available is not None:
                lb.lessons_available = int(lessons_available)
            elif delta is not None:
                lb.lessons_available += int(delta)
                if lb.lessons_available < 0:
                    lb.lessons_available = 0
            
            lb.save()

            # Автоматически меняем роль с APPLICANT на STUDENT при начислении баланса
            role_changed = False
            if student.role == User.Roles.APPLICANT and lb.lessons_available > 0:
                student.role = User.Roles.STUDENT
                student.save(update_fields=['role'])
                role_changed = True

            AuditLog.objects.create(
                actor=request.user,
                action="MANAGER_UPDATE_BALANCE",
                meta={
                    "student_id": student.id,
                    "student_email": student.email,
                    "old_balance": old_balance,
                    "new_balance": lb.lessons_available,
                    "old_role": old_role,
                    "new_role": student.role,
                    "role_changed": role_changed,
                    "delta": delta,
                    "lessons_available": lessons_available,
                },
            )

        return Response(ManagerBalanceSerializer(lb).data)
