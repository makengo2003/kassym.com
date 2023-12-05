from rest_framework import serializers
from base_object_presenter.models import BaseModelPresenter


class BaseSerializerPresenter:
    def __init__(self, model_presenter: BaseModelPresenter, serializer_name: str):
        self.model_presenter = model_presenter
        self.serializer_name = serializer_name

    def __call__(self, *args, **kwargs):
        return BaseSerializer(model_presenter=self.model_presenter, serializer_name=self.serializer_name,
                              *args, **kwargs)


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = None

    def __init__(self, *args, **kwargs):
        self.model_presenter = kwargs.pop("model_presenter")
        self.serializer_name = kwargs.pop("serializer_name")
        instance = kwargs.get('instance', None)

        self.Meta.model = self.model_presenter.model
        self.Meta.fields = getattr(self.model_presenter, "get_" + self.serializer_name + "_serializer_fields")()

        super().__init__(*args, **kwargs)

        for field_name, field in (
                getattr(self.model_presenter, f"get_{self.serializer_name}_serializer_extra_fields")().items()):
            self.fields[field_name] = field

            if instance:
                field_value = getattr(instance, field_name, None)
                self.fields[field_name].default = field_value
                self.fields[field_name].initial = field_value

    def create(self, validated_data):
        return self.model_presenter.object_add_form_serializer_create(validated_data)

    def update(self, instance, validated_data):
        return self.model_presenter.object_edit_form_serializer_update(instance, validated_data)
