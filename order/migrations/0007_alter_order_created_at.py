# Generated by Django 4.1.5 on 2023-11-17 04:14

from django.db import migrations, models
import project.utils


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_order_company_name_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(default=project.utils.datetime_now, editable=False),
        ),
    ]
