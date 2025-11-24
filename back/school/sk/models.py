from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Payment(models.Model):
    """
    Оплата от ученика (или его родителя). По ТЗ менеджер начисляет занятия после оплаты.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    package_name = models.CharField(max_length=120, blank=True)  # название пакета/тарифа
    paid_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)  # менеджер/админ подтвердил оплату

    def __str__(self):
        return f"Payment {self.id} {self.student} {self.amount} ({'OK' if self.confirmed else 'PENDING'})"


class LessonBalance(models.Model):
    """
    Баланс занятий ученика (сколько доступно списать).
    """
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lesson_balance')
    lessons_available = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Balance({self.student}): {self.lessons_available}"


class Lesson(models.Model):
    """
    Карточка урока — соответствует ТЗ (ученик, родитель, преподаватель, ссылка и пр.).
    """
    STATUS = (
        ("PLANNED", "Запланирован"),
        ("DONE", "Проведён"),
        ("CANCELLED", "Отменён"),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons_as_student')
    parent_full_name = models.CharField(max_length=255, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons_as_teacher')
    link = models.URLField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="PLANNED")
    comment = models.TextField(blank=True)

    # Снималось ли занятие с баланса (при назначении/проведении)
    debited_from_balance = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lesson #{self.id} {self.student} with {self.teacher} ({self.status})"


class AuditLog(models.Model):
    """
    Простейший аудит действий в админ-кабинете.
    """
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    action = models.CharField(max_length=120)      # e.g., 'SET_ROLE', 'CONFIRM_PAYMENT', 'CREATE_LESSON' ...
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.actor} -> {self.action}"
