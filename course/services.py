import os
from pathlib import Path
from typing import IO, Generator, Mapping, Tuple

from django.db.models import QuerySet
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from project import settings
from .models import Course, Lesson
from .serializers import CourseFormSerializer, CoursesSerializer, CourseSerializer


def get_courses() -> CoursesSerializer:
    courses = Course.objects.all().only("id", "name")
    return CoursesSerializer(courses, many=True)


def get_course(course_id: int) -> CourseSerializer:
    course = Course.objects.filter(id=course_id).prefetch_related("lessons").first()
    return CourseSerializer(course)


def add_course(data: Mapping, files) -> None:
    serializer = CourseFormSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(files=files)


def edit_course(course_id: int, data: Mapping, files) -> None:
    course = get_object_or_404(Course, id=course_id)
    serializer = CourseFormSerializer(course, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(files=files)


def delete_course(course_id: int) -> None:
    course = Course.objects.filter(id=course_id).prefetch_related("lessons").first()

    for lesson in course.lessons.all():
        video_path = os.path.join(settings.MEDIA_ROOT, str(lesson.video))

        if os.path.isfile(video_path):
            os.remove(video_path)

    course.delete()


def get_courses_page(language: str) -> QuerySet[Course]:
    return Course.objects.filter(is_available=True, language=language.upper()).prefetch_related("lessons")


def get_lesson_page(lesson_id: int) -> Tuple[Course, QuerySet[Lesson], Lesson]:
    if not lesson_id:
        lesson_id = 0
        
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lessons = Lesson.objects.filter(course=lesson.course)
    return lesson.course, lessons, lesson


def ranged(file: IO[bytes], start: int = 0, end: int = None, block_size: int = 8192) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)
    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size
        if data_length <= 0:
            break
        data = file.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(file, 'close'):
        file.close()


def get_stream(request, lesson_id):
    if not request.user.is_authenticated:
        return HttpResponse("403 Forbidden")

    request_referer = request.META.get("HTTP_REFERER", "").replace("https://", "").replace("http://", "")
    if request_referer != settings.SITE_DOMAIN + f"/lesson/?id={lesson_id}":
        return HttpResponse("Скачать видео невозможно!")

    video = get_object_or_404(Lesson, id=lesson_id).video

    path = Path(video.path)

    file = path.open('rb')
    file_size = path.stat().st_size

    content_length = file_size
    status_code = 200
    content_range = request.headers.get("range")

    if content_range is not None:
        content_ranges = content_range.strip().lower().split('=')[-1]
        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
        content_length = (range_end - range_start) + 1
        file = ranged(file, start=range_start, end=range_end + 1)
        status_code = 206
        content_range = f'bytes {range_start}-{range_end}/{file_size}'

    # return file, status_code, content_length, content_range

    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')

    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range

    return response
