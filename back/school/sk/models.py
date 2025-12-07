from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    """
    Оплата от ученика (или его родителя).
    Менеджер/админ после оплаты подтверждает её и начисляет занятия на баланс.
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    package_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Название пакета/тарифа",
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(
        default=False,
        help_text="Оплата подтверждена (начислены занятия)",
    )

    def __str__(self):
        return f"Payment(id={self.id}, student={self.student}, amount={self.amount}, confirmed={self.confirmed})"


class LessonBalance(models.Model):
    """
    Баланс доступных занятий у ученика.
    """
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lesson_balance",
    )
    lessons_available = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LessonBalance(student={self.student}, lessons_available={self.lessons_available})"


class Lesson(models.Model):
    """
    Урок / занятие.

    Через него мы:
    - строим расписание,
    - считаем отчёты,
    - списываем занятия с баланса.
    """

    STATUS_PLANNED = "PLANNED"
    STATUS_DONE = "DONE"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PLANNED, "Запланировано"),
        (STATUS_DONE, "Проведено"),
        (STATUS_CANCELLED, "Отменено"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons_as_student",
    )
    # ФИО родителя фиксируем на момент создания урока
    parent_full_name = models.CharField(max_length=255, blank=True)

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons_as_teacher",
    )

    link = models.CharField(
        max_length=300,
        blank=True,
        help_text="Ссылка на урок (Zoom/Discord/и т.п.)",
    )

    scheduled_at = models.DateTimeField(
        help_text="Дата и время начала урока",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
    )

    comment = models.TextField(blank=True)
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Причина отмены занятия (заполняется при статусе CANCELLED)",
    )
    feedback = models.TextField(
        blank=True,
        help_text="Обратная связь по занятию (заполняется при статусе DONE)",
    )
    debited_from_balance = models.BooleanField(
        default=False,
        help_text="True, если занятие уже списано с баланса",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lesson(id={self.id}, student={self.student}, teacher={self.teacher}, at={self.scheduled_at}, status={self.status})"


class AuditLog(models.Model):
    """
    Лог действий админов/менеджеров/учителей.
    Можно потом строить историю изменений.
    """
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=120)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AuditLog(action={self.action}, actor={self.actor}, created_at={self.created_at})"


class Course(models.Model):
    """
    Курс/направление (Python, Roblox, и т.п.).
    Можно использовать для тарифов и пакетов.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Значения по умолчанию для пакета:
    default_lessons = models.PositiveIntegerField(default=4)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title


class StudentProfile(models.Model):
    """
    Профиль ученика для геймификации (уровень, XP, внутренняя валюта сезона).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    season_currency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"StudentProfile({self.user}): lvl={self.level}, xp={self.xp}"
