from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings


@receiver(post_migrate)
def create_root_admin(sender, **kwargs):
    """
    Создание 'вшитого' администратора при первом запуске.
    """
    User = get_user_model()
    root_email = getattr(settings, "ROOT_ADMIN_EMAIL", None)

    if not root_email:
        return

    user, created = User.objects.get_or_create(email=root_email)
    if created:
        user.set_password("admin123")   # можно поменять
    user.role = "ADMIN"
    user.is_staff = True
    user.is_superuser = True
    user.save()
