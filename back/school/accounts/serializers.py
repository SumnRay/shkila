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
    class Meta:
        model = User
        fields = ("id", "email", "phone", "student_full_name",
                  "parent_full_name", "role", "is_staff", "is_superuser")
