import functools
import json
from typing import MutableMapping

from django.db.models import Q
from rest_framework.exceptions import ValidationError

from .models import BaseModelPresenter
from .serializers import BaseSerializerPresenter, BaseSerializer


class BaseServicesPresenter:
    model_presenter: BaseModelPresenter

    def __init__(self):
        self.serializers = {
            "objects": BaseSerializerPresenter(self.model_presenter, "objects"),
            "object_add_form": BaseSerializerPresenter(self.model_presenter, "object_add_form"),
            "object_edit_form": BaseSerializerPresenter(self.model_presenter, "object_edit_form"),
            "object": BaseSerializerPresenter(self.model_presenter, "object"),
        }

    def get_many(self, get_many_request_schema: MutableMapping) -> BaseSerializer:
        ordering = get_many_request_schema.get("ordering", [])
        if type(ordering) == str:
            ordering = json.loads(get_many_request_schema.get("ordering", "[]"))

        filtration = get_many_request_schema.get("filtration", {})
        if type(filtration) == str:
            filtration = json.loads(get_many_request_schema.get("filtration", "{}"))

        searching = get_many_request_schema.get("searching", {})
        if type(searching) == str:
            searching = json.loads(get_many_request_schema.get("searching", "{}"))

        offset = get_many_request_schema.get("offset", 0)
        limit = get_many_request_schema.get("limit", None)

        words = searching.get("text", "").split()
        searching_filters = []
        searchable_fields = self.model_presenter.get_searchable_fields()

        for searching_field in searching.get("searching_fields", []):
            if searching_field.get("field_name") in searchable_fields:
                if searching_field.get("with__icontains"):
                    if searching_field.get("each_word"):
                        for query in words:
                            searching_filters.append(Q(**{f"{searching_field['field_name']}__icontains": query.lower()}))
                    else:
                        searching_filters.append(Q(**{f'{searching_field["field_name"]}__icontains': searching["text"].lower()}))
                else:
                    searching_filters.append(Q(**{searching_field["field_name"]: searching["text"].lower()}))

        if len(searching_filters) > 0:
            searching_filtration = functools.reduce(lambda a, b: a | b, searching_filters)
        else:
            searching_filtration = Q()

        get_many_query = self.model_presenter.get_many_service()
        objects = (self.model_presenter.model.objects
                   .prefetch_related(*get_many_query["prefetch_related"])
                   .select_related(*get_many_query["select_related"])
                   .filter(searching_filtration, **{**get_many_query.get("filtration"), **filtration})
                   .annotate(**get_many_query["annotate"])
                   .order_by(*ordering)
                   .only(*get_many_query["only"])
                   .distinct()[offset:limit])

        return self.serializers["objects"](objects, many=True)

    def get(self, obj_id: int) -> BaseSerializer:
        get_query = self.model_presenter.get_service()

        obj = (self.model_presenter.model.objects
               .prefetch_related(*get_query["prefetch_related"])
               .select_related(*get_query["select_related"])
               .filter(id=obj_id)
               .annotate(**get_query["annotate"])
               .only(*get_query["only"])
               .first())

        return self.serializers["object"](obj)

    def delete(self, obj_id: int) -> None:
        self.model_presenter.model.objects.filter(id=obj_id).delete()

    def add(self, add_request_schema: MutableMapping) -> int:
        serializer = self.serializers["object_add_form"](data=add_request_schema)
        serializer.is_valid(raise_exception=True)
        return serializer.save().id

    def edit(self, obj_id: int, edit_request_schema: MutableMapping) -> None:
        obj = self.model_presenter.model.objects.filter(id=obj_id).first()
        serializer = self.serializers["object_edit_form"](obj, data=edit_request_schema)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def update_fields(self, obj_id: int, data: MutableMapping) -> None:
        updatable_fields = self.model_presenter.get_updatable_fields()

        for key, value in data.items():
            if key not in updatable_fields:
                raise ValidationError({'detail': f'Not updatable field "{key}"'})
            else:
                try:
                    self.model_presenter.model._meta.get_field(key).clean(value, None)
                except Exception as e:
                    raise ValidationError({'detail': e})

        self.model_presenter.model.objects.filter(id=obj_id).update(**data)
