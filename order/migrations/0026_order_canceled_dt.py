# Generated by Django 4.1.5 on 2023-12-10 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0025_order_cancellation_reason_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='canceled_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
