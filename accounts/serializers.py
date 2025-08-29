import uuid
from rest_framework import serializers
from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
            "role",
            "company",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "role": {"required": False},
            "company": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        # Auto-generate username
        base_username = validated_data["email"].split("@")[0]
        unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"
        validated_data["username"] = unique_username

        # If public registration → force EMPLOYEE role
        if not user or not user.is_authenticated:
            validated_data["role"] = User.Role.EMPLOYEE
            validated_data["company"] = None

        # If Manager creates a user, restrict company
        elif user.role == User.Role.MANAGER:
            validated_data["company"] = user.company

        # Admin can assign freely

        return User.objects.create_user(**validated_data)
