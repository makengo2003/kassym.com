# Generated by Django 4.1.5 on 2023-03-27 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_height_product_length_product_width'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='vendor_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
