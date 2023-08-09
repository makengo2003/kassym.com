from rest_framework import serializers


class CourseIdSchema(serializers.Serializer):
    course_id = serializers.IntegerField()


class CourseJustIdSchema(serializers.Serializer):
    id = serializers.IntegerField()
