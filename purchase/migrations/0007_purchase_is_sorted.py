# Generated by Django 4.1.5 on 2023-11-23 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0006_alter_purchase_last_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='is_sorted',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
