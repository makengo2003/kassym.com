# Generated by Django 4.1.5 on 2023-11-21 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_product_market'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='market',
            field=models.CharField(blank=True, choices=[('sadovod', 'Sadovod'), ('yuzhnye_vorota', 'Yuzhnye_vorota')], max_length=255, null=True),
        ),
    ]
