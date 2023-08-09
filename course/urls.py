from django.urls import path
from . import views


urlpatterns = [
    path("get_courses/", views.get_courses_view, name="get_courses"),
    path("get_course/", views.get_course_view, name="get_course"),
    path("add_course/", views.add_course_view, name="add_course"),
    path("edit_course/", views.edit_course_view, name="edit_course"),
    path("delete_course/", views.delete_course_view, name="delete_course"),
    path("video_stream/", views.video_stream_view, name="video_stream")
]
