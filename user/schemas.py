from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class LoginRequestSchema(serializers.Serializer):
    username = PhoneNumberField(error_messages={"invalid": "Введите правильный номер телефона!"})
    password = serializers.CharField(max_length=50)
    favourite_products = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=False)


class ClientIdSchema(serializers.Serializer):
    client_id = serializers.IntegerField()
