# Generated by Django 4.1.5 on 2023-10-24 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_favouriteproduct_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=255)),
            ],
        ),
    ]