import base64
import os
from typing import Mapping
from django.contrib.auth.models import User
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from user.models import Client


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=50)
    new_password1 = serializers.CharField(max_length=50)
    new_password2 = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]

    def validate_old_password(self, old_password: str) -> str:
        if self.instance:
            if not self.instance.check_password(old_password):
                raise serializers.ValidationError({"old_password": "Старый пароль неверный"})
        return old_password

    def validate(self, attrs: Mapping) -> Mapping:
        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Указанные пароли не совпадают"})
        elif attrs["new_password1"] == attrs["old_password"]:
            raise serializers.ValidationError({"new_password1": "Новый пароль совпадает со старым паролем"})
        return attrs

    def update(self, user: User, validated_data: Mapping) -> User:
        user.set_password(validated_data.get("new_password1"))
        user.save(update_fields=["password"])

        if hasattr(user, "client"):
            user.client.password = validated_data.get("new_password1")
            user.client.save(update_fields=["password"])

        return user


class ClientSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="account.username")
    is_expired = serializers.BooleanField()

    class Meta:
        model = Client
        fields = "__all__"


class ClientFormSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField()

    class Meta:
        model = Client
        fields = ["fullname", "phone_number", "expires_at", "company_name", "device1", "device2", "device3"
                  "ignore_device_verification"]

    def create(self, validated_data):
        if User.objects.filter(username=validated_data["phone_number"]).exists():
            raise serializers.ValidationError({"phone_number": ["Пользователь с данным номером телефона уже есть"]})

        password = "qwerty1234"  # base64.b64encode(os.urandom(8)).decode().replace("/", "a").replace("=", "b").replace("+", "c")
        account = User.objects.create_user(validated_data.pop("phone_number"), password=password)
        return Client.objects.create(account=account, fullname=validated_data.pop("fullname"), password=password,
                                     company_name=validated_data.pop("company_name"),
                                     expires_at=validated_data.pop("expires_at"),
                                     ignore_device_verification=validated_data.pop("ignore_device_verification"))

    def update(self, client, validated_data):
        if validated_data["phone_number"] != client.account.username:
            if User.objects.filter(username=validated_data["phone_number"]).exists():
                raise serializers.ValidationError({"phone_number": ["Пользователь с данным номером телефона уже есть"]})

        client.account.username = validated_data.pop("phone_number")
        client.account.save(update_fields=["username"])

        client.fullname = validated_data.pop("fullname")
        client.expires_at = validated_data.pop("expires_at")
        client.company_name = validated_data.pop("company_name")
        client.device1 = validated_data.pop("device1")
        client.device2 = validated_data.pop("device2")
        client.device3 = validated_data.pop("device3")
        client.ignore_device_verification = validated_data.pop("ignore_device_verification")
        client.save(update_fields=["fullname", "expires_at", "company_name", "device1", "device2", "device3", "ignore_device_verification"])

        return client
