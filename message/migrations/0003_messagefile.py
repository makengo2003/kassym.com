# Generated by Django 4.1.5 on 2024-01-03 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0002_alter_message_dt_alter_message_from_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='message_files/')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.message')),
            ],
        ),
    ]
