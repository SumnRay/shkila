from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdminRole
from .models import Payment, Lesson, LessonBalance, AuditLog, Course, Module, LessonTopic
from .admin_serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminSetRoleSerializer,
    PaymentSerializer,
    LessonSerializer,
    AdminLessonCreateSerializer,
    AdminLessonUpdateSerializer,
    LessonBalanceSerializer,
    AuditLogSerializer,
    CourseSerializer,
    CourseCreateUpdateSerializer,
    ModuleSerializer,
    ModuleCreateUpdateSerializer,
    LessonTopicSerializer,
    LessonTopicCreateUpdateSerializer,
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
    queryset = User.objects.all().order_by("-date_joined")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role", "is_superuser"]
    search_fields = ["email", "student_full_name", "parent_full_name"]
    ordering_fields = ["id", "email", "date_joined"]


class AdminUserByEmailAPI(APIView):
    """
    Поиск пользователя по email для создания урока.
    GET /api/admin/users/by-email/?email=user@example.com
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

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


class AdminUserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/users/{id}/      — детальная инфа
    PATCH  /api/admin/users/{id}/      — редактирование (email, phone, ФИО)
    DELETE /api/admin/users/{id}/      — удаление пользователя
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserDetailSerializer

    def perform_update(self, serializer):
        old_email = serializer.instance.email
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="UPDATE_USER",
            meta={
                "user_id": user.id,
                "old_email": old_email,
                "new_email": user.email,
            },
        )

    def perform_destroy(self, instance):
        user_id = instance.id
        email = instance.email
        instance.delete()
        AuditLog.objects.create(
            actor=self.request.user,
            action="DELETE_USER",
            meta={"user_id": user_id, "email": email},
        )


class AdminSetRoleAPI(APIView):
    """
    Назначение роли пользователю: PATCH /api/admin/users/{id}/set-role/
    body: {"role": "TEACHER"}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        from django.conf import settings
        from accounts.permissions import is_root_admin
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)

        # защищаем root admin — ему нельзя менять роль
        if is_root_admin(user):
            return Response({"detail": "cannot change role of ROOT ADMIN"}, status=400)

        ser = AdminSetRoleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new_role = ser.validated_data["role"]

        user.role = new_role
        user.is_staff = new_role == "ADMIN"
        if new_role == "ADMIN":
            user.is_superuser = False  # суперюзер только у root-admin
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
    queryset = Payment.objects.select_related("student").all().order_by("-paid_at")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["confirmed", "student"]
    ordering_fields = ["paid_at", "amount", "id"]


class AdminPaymentConfirmAPI(APIView):
    """
    Подтверждение оплаты и начисление занятий на баланс.
    POST /api/admin/payments/{id}/confirm/
    body: {"lessons_to_add": 4}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

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

            payment.confirmed = True
            payment.save()

            AuditLog.objects.create(
                actor=request.user,
                action="CONFIRM_PAYMENT",
                meta={
                    "payment_id": payment.id,
                    "student": payment.student_id,
                    "lessons_added": lessons_to_add,
                },
            )

        return Response({"detail": "ok"})


class AdminBalanceGetAPI(generics.RetrieveAPIView):
    """
    Получить текущий баланс занятий ученика:
    GET /api/admin/students/{student_id}/balance/
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = LessonBalanceSerializer
    lookup_field = "student"
    lookup_url_kwarg = "student_id"

    def get_queryset(self):
        return LessonBalance.objects.select_related("student").all()


# ======= LESSONS =======


class AdminLessonListAPI(generics.ListCreateAPIView):
    """
    GET: список занятий (фильтры: status, student, teacher)
    POST: создать занятие (назначить)
    Может использовать student_email и teacher_email вместо ID.
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "student", "teacher"]
    ordering_fields = ["scheduled_at", "created_at", "id"]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminLessonCreateSerializer
        return LessonSerializer

    def get_queryset(self):
        return Lesson.objects.select_related("student", "teacher", "course").all().order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        lesson = serializer.save()
        # Автоматически заполняем parent_full_name из профиля ученика, если не указано
        if not lesson.parent_full_name and lesson.student:
            lesson.parent_full_name = lesson.student.parent_full_name or ''
            lesson.save(update_fields=['parent_full_name'])
        AuditLog.objects.create(
            actor=self.request.user,
            action="CREATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "student_email": lesson.student.email,
                "teacher": lesson.teacher_id,
                "teacher_email": lesson.teacher.email if lesson.teacher else None,
                "scheduled_at": lesson.scheduled_at.isoformat(),
            },
        )


class AdminLessonUpdateAPI(generics.UpdateAPIView):
    """
    Частичное обновление урока админом:
    PATCH /api/admin/lessons/{id}/
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = AdminLessonUpdateSerializer
    queryset = Lesson.objects.select_related("student", "teacher", "course").all()
    http_method_names = ["patch", "options", "head"]

    def perform_update(self, serializer):
        lesson = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="UPDATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "teacher": lesson.teacher_id,
                "status": lesson.status,
            },
        )


class AdminLessonDebitAPI(APIView):
    """
    Списание занятия с баланса:
    POST /api/admin/lessons/{id}/debit/
    body: {"mark_done": true/false}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

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
                action="DEBIT_LESSON",
                meta={
                    "lesson_id": les.id,
                    "student": les.student_id,
                    "mark_done": mark_done,
                },
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


# ======= COURSES =======


class AdminCourseListCreateAPI(generics.ListCreateAPIView):
    """
    GET: список всех курсов
    POST: создать новый курс
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def get_queryset(self):
        return Course.objects.prefetch_related('modules__topics').all().order_by('id')

    def create(self, request, *args, **kwargs):
        """Переопределяем create, чтобы возвращать полные данные курса после создания"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Возвращаем полные данные курса с модулями
        full_serializer = CourseSerializer(serializer.instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class AdminCourseDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: детали курса с модулями и темами
    PATCH: обновить курс
    DELETE: удалить курс
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Course.objects.prefetch_related('modules__topics').all()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def update(self, request, *args, **kwargs):
        """Переопределяем update, чтобы возвращать полные данные курса после обновления"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем полные данные курса с модулями
        full_serializer = CourseSerializer(instance)
        return Response(full_serializer.data)


# ======= MODULES =======


class AdminModuleListCreateAPI(generics.ListCreateAPIView):
    """
    GET: список модулей курса
    POST: создать новый модуль в курсе
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ModuleCreateUpdateSerializer
        return ModuleSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(course_id=course_id).prefetch_related('topics').order_by('order', 'id')
        return Module.objects.prefetch_related('topics').all().order_by('order', 'id')

    def perform_create(self, serializer):
        course_id = self.request.data.get('course_id') or self.request.query_params.get('course_id')
        if not course_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "course_id is required"})
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Course not found")
        module = serializer.save(course=course)
        AuditLog.objects.create(
            actor=self.request.user,
            action="CREATE_MODULE",
            meta={
                "module_id": module.id,
                "course_id": course.id,
                "module_title": module.title,
            },
        )

    def create(self, request, *args, **kwargs):
        """Переопределяем create, чтобы возвращать полные данные модуля после создания"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Возвращаем полные данные модуля с темами
        full_serializer = ModuleSerializer(serializer.instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class AdminModuleDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: детали модуля с темами
    PATCH: обновить модуль
    DELETE: удалить модуль
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Module.objects.prefetch_related('topics').all()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return ModuleCreateUpdateSerializer
        return ModuleSerializer

    def update(self, request, *args, **kwargs):
        """Переопределяем update, чтобы возвращать полные данные модуля после обновления"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем полные данные модуля с темами
        full_serializer = ModuleSerializer(instance)
        return Response(full_serializer.data)


# ======= LESSON TOPICS =======


class AdminLessonTopicListCreateAPI(generics.ListCreateAPIView):
    """
    GET: список тем модуля
    POST: создать новую тему в модуле
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonTopicCreateUpdateSerializer
        return LessonTopicSerializer

    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        if module_id:
            return LessonTopic.objects.filter(module_id=module_id).order_by('order', 'id')
        return LessonTopic.objects.all().order_by('order', 'id')

    def perform_create(self, serializer):
        module_id = self.request.data.get('module_id') or self.request.query_params.get('module_id')
        if not module_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "module_id is required"})
        try:
            module = Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Module not found")
        topic = serializer.save(module=module)
        AuditLog.objects.create(
            actor=self.request.user,
            action="CREATE_LESSON_TOPIC",
            meta={
                "topic_id": topic.id,
                "module_id": module.id,
                "topic_title": topic.title,
            },
        )

    def create(self, request, *args, **kwargs):
        """Переопределяем create, чтобы возвращать полные данные темы после создания"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Возвращаем полные данные темы
        full_serializer = LessonTopicSerializer(serializer.instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class AdminLessonTopicDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: детали темы
    PATCH: обновить тему
    DELETE: удалить тему
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = LessonTopic.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return LessonTopicCreateUpdateSerializer
        return LessonTopicSerializer

    def update(self, request, *args, **kwargs):
        """Переопределяем update, чтобы возвращать полные данные темы после обновления"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем полные данные темы
        full_serializer = LessonTopicSerializer(instance)
        return Response(full_serializer.data)
