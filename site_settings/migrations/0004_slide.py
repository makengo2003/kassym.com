# Generated by Django 4.1.5 on 2023-10-24 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0003_alter_contact_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='slide_images/')),
                ('link', models.CharField(default='/', max_length=500)),
            ],
        ),
    ]
