from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("id", "is_staff")

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user_model = get_user_model()
            user = user_model.objects.filter(email=email).first()

            if user and user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                data["user"] = user
                data["token"] = token.key
            else:
                raise serializers.ValidationError(
                    "Invalid credentials. Please try again."
                )
        else:
            raise serializers.ValidationError(
                "Enter your e-mail address and password."
            )

        return data
