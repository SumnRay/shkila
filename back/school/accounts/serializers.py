from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    parent_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email", "phone", "student_full_name", "parent_full_name",
            "password", "parent_password"
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated):
        user = User(
            email=validated["email"].lower(),
            username=validated["email"].lower(),
            phone=validated.get("phone", ""),
            student_full_name=validated.get("student_full_name", ""),
            parent_full_name=validated.get("parent_full_name", ""),
            role=User.Roles.APPLICANT,  # по умолчанию — абитуриент
        )
        user.set_password(validated["password"])
        user.parent_password_hash = make_password(validated["parent_password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class MeSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ("id", "email", "phone", "student_full_name",
                  "parent_full_name", "role", "role_display", "is_staff", "is_superuser")


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""
    class Meta:
        model = User
        fields = ("email", "phone", "student_full_name", "parent_full_name")
    
    def validate_email(self, value):
        # Проверяем, что email уникален (кроме текущего пользователя)
        user = self.instance
        if User.objects.filter(email=value.lower()).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value.lower()
