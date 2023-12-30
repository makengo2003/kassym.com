# Generated by Django 4.1.5 on 2023-12-30 07:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import project.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('message', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='dt',
            field=models.DateTimeField(default=project.utils.datetime_now, editable=False),
        ),
        migrations.AlterField(
            model_name='message',
            name='from_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='messages_from_me', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='has_read',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
