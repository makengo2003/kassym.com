# Generated by Django 4.1.5 on 2023-11-29 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0011_purchase_purchased_dt'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='sorted_report',
            field=models.ImageField(blank=True, null=True, upload_to='order_is_sorted_reports/'),
        ),
    ]
