from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response

from project.utils import request_schema_validation
from user.permission_classes import IsAdmin
from . import services, schemas


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_courses_view(_) -> Response:
    courses = services.get_courses()
    return Response(courses.data)


@api_view(["GET"])
@permission_classes([IsAdmin])
@request_schema_validation("GET", schemas.CourseIdSchema)
def get_course_view(request: Request) -> Response:
    course = services.get_course(request.query_params.get("course_id"))
    return Response(course.data)


@api_view(["POST"])
@permission_classes([IsAdmin])
@parser_classes([MultiPartParser, FormParser])
def add_course_view(request: Request) -> Response:
    services.add_course(request.data, request.FILES)
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAdmin])
@parser_classes([MultiPartParser, FormParser])
@request_schema_validation("POST", schemas.CourseJustIdSchema)
def edit_course_view(request: Request) -> Response:
    services.edit_course(request.data.get("id"), request.data, request.FILES)
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAdmin])
@request_schema_validation("POST", schemas.CourseIdSchema)
def delete_course_view(request: Request) -> Response:
    services.delete_course(request.data.get("course_id"))
    return Response({"success": True})


def video_stream_view(request):
    lesson_id = request.GET.get("lesson_id", 0)
    return services.get_stream(request, lesson_id)
