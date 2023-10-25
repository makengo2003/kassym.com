import json
from typing import Sequence

from .models import Contact, Slide
from .serializers import ContactSerializer


def get_contacts() -> ContactSerializer:
    contacts = Contact.objects.all()
    return ContactSerializer(contacts, many=True)


def save_contacts(contacts: Sequence) -> None:
    Contact.objects.bulk_create([Contact(**contact) for contact in contacts],
                                update_conflicts=True, update_fields=["contact", "link"], unique_fields=["type"])


def get_about_us_text():
    with open("site_settings/about_us.txt") as file:
        about_us = file.read()

    return about_us


def save_about_us_text(text: str) -> None:
    with open("site_settings/about_us.txt", "w") as file:
        file.write(text)


def get_guarantee_file():
    with open("site_settings/guarantee.txt") as file:
        guarantee_file = file.read()

    return open(guarantee_file, 'rb')


def save_guarantee_text(files: Sequence = None) -> None:
    if files:
        file = files[next(iter(files))]
        file_path = 'static/' + file.name

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        with open("site_settings/guarantee.txt", "w") as file:
            file.write(file_path)


def get_slides():
    return Slide.objects.all().values()


def save_slides(form_data, files):
    slides = []

    for slide in json.loads(form_data["slides"]):
        slide_image = slide.get("image")
        if slide_image:
            img = files.get("image: " + slide_image, False)

            if not img:
                img = slide["image"].replace("/media/", "")

            slide.pop("image")
            slides.append(Slide(**slide, image=img))

    Slide.objects.all().delete()
    Slide.objects.bulk_create(slides)
