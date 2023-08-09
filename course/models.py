from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Course(models.Model):
    language = models.CharField(choices=(("RU", "Рус"), ("KZ", "Қаз")), max_length=5)
    is_available = models.BooleanField(default=False)
    poster = models.ImageField(upload_to="course_posters/")
    name = models.CharField(max_length=500)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    name = models.CharField(max_length=500)
    video = models.FileField(upload_to="course_videos/")
