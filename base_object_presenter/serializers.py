from rest_framework import serializers
from base_object_presenter.models import BaseModelPresenter


class BaseSerializerPresenter:
    def __init__(self, model_presenter: BaseModelPresenter, serializer_name: str):
        self.model_presenter = model_presenter
        self.serializer_name = serializer_name

    def __call__(self, *args, **kwargs):
        return BaseSerializer(model_presenter=self.model_presenter, serializer_name=self.serializer_name,
                              *args, **kwargs)


# Define a custom metaclass for your serializer
class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = None

    def __init__(self, *args, **kwargs):
        self.model_presenter = kwargs.pop("model_presenter")
        self.serializer_name = kwargs.pop("serializer_name")

        self.Meta.model = self.model_presenter.model
        self.Meta.fields = getattr(self.model_presenter, "get_" + self.serializer_name + "_serializer_fields")()

        for field_name, field in (
                getattr(self.model_presenter, f"get_{self.serializer_name}_serializer_extra_fields")().items()):
            setattr(self, field_name, field)

        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return getattr(self.model_presenter, f"{self.serializer_name}_serializer_create")(validated_data)

    def update(self, instance, validated_data):
        return getattr(self.model_presenter, f"{self.serializer_name}_serializer_update")(instance, validated_data)
