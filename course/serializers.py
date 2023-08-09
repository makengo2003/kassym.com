import os
import urllib.parse
from typing import MutableMapping

from django.db.models import Q

from course.models import Course, Lesson
from rest_framework import serializers

from project import settings


class CourseFormSerializer(serializers.ModelSerializer):
    lessons = serializers.JSONField(required=False)
    poster = serializers.CharField(max_length=1000)

    class Meta:
        model = Course
        fields = "__all__"

    def create(self, validated_data: MutableMapping):
        lessons = validated_data.pop("lessons")
        files = validated_data.pop("files")
        poster = validated_data.pop("poster")
        course = Course(**validated_data, poster=files[poster])

        orm_lessons = []
        for lesson in lessons:
            orm_lessons.append(Lesson(course=course, name=lesson["name"], video=files.get(lesson.get("video"))))

        course.save()
        Lesson.objects.bulk_create(orm_lessons)

        return course

    def update(self, course, validated_data):
        lessons = validated_data.pop("lessons")
        files = validated_data.pop("files")

        poster = validated_data.pop("poster")
        Course.objects.filter(id=course.id).update(**validated_data, poster=files.get(poster, course.poster))

        if not poster.startswith("/media/"):
            Course.objects.filter(id=course.id).update(poster="course_posters/" + poster)

        orm_lessons = []
        # videos = []

        for lesson in lessons:
            lesson_video = lesson.pop("video")
            video = files.get(lesson_video, False)

            if not video:
                video = urllib.parse.unquote(lesson_video.replace("/media/", "").replace("%25", "%"), encoding='utf-8')
                # videos.append(video)

            orm_lessons.append(Lesson(**lesson, course=course, video=video))

        # lessons = Lesson.objects.filter(~Q(video__in=videos), course=course).only("video")
        # for lesson in lessons:
        #     video_path = os.path.join(settings.MEDIA_ROOT, str(lesson.video))

        #     if os.path.isfile(video_path):
        #         os.remove(video_path)

        Lesson.objects.filter(course=course).delete()
        Lesson.objects.bulk_create(orm_lessons)

        return course


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["name", "video"]


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Course
        fields = "__all__"


class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name", "language"]
