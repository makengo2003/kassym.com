# Generated by Django 4.1.5 on 2023-10-24 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_client_ignore_device_verification'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favouriteproduct',
            unique_together=set(),
        ),
    ]
