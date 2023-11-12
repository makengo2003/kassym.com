from django.contrib.auth.models import User
from base_object_presenter.models import BaseModelPresenter


class StaffModelPresenter(BaseModelPresenter):
    model = User

    @staticmethod
    def get_many_service():
        return {
            "prefetch_related": [],
            "select_related": [],
            "annotate": {},
            "only": ["id", "username", "first_name", "last_name"],
            "filtration": {"is_staff": True, "is_superuser": False}
        }

    @staticmethod
    def get_service():
        return {
            "prefetch_related": [],
            "select_related": [],
            "annotate": {},
            "only": ["id", "username", "first_name", "last_name"],
        }

    @staticmethod
    def get_object_serializer_fields():
        return ["id", "username", "first_name", "last_name"]

    @staticmethod
    def get_objects_serializer_fields():
        return ["id", "username", "first_name", "last_name"]

    @staticmethod
    def get_object_add_form_serializer_fields():
        return ["username", "first_name", "last_name"]

    def object_add_form_serializer_create(self, validated_data):
        return self.model.objects.create_user(**validated_data, password="qwerty1234", is_staff=True)
