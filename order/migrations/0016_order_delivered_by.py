# Generated by Django 4.1.5 on 2023-11-27 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0015_order_is_sorted_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivered_by',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
