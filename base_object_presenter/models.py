from django.db import models


class BaseModelPresenter:
    model: models.Model

    @staticmethod
    def get_many_service():
        return {
            "prefetch_related": [],
            "select_related": [],
            "annotate": {},
            "only": [],
            "filtration": {}
        }

    @staticmethod
    def get_service():
        return {
            "prefetch_related": [],
            "select_related": [],
            "annotate": {},
            "only": [],
        }

    @staticmethod
    def get_object_serializer_fields():
        return "__all__"

    @staticmethod
    def get_object_serializer_extra_fields():
        return {}

    @staticmethod
    def get_objects_serializer_fields():
        return "__all__"

    @staticmethod
    def get_objects_serializer_extra_fields():
        return {}

    @staticmethod
    def get_object_add_form_serializer_fields():
        return "__all__"

    @staticmethod
    def get_object_add_form_serializer_extra_fields():
        return {}

    @staticmethod
    def get_object_edit_form_serializer_fields():
        return "__all__"

    @staticmethod
    def get_object_edit_form_serializer_extra_fields():
        return {}

    def object_edit_form_serializer_update(self, instance, validated_data):
        return self.model.objects.filter(id=instance.id).update(**validated_data)

    def object_add_form_serializer_create(self, validated_data):
        return self.model.objects.create(**validated_data)

    @staticmethod
    def get_updatable_fields():
        return []

    @staticmethod
    def get_searchable_fields():
        return []
