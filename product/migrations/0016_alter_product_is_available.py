# Generated by Django 4.1.5 on 2023-12-19 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_product_card_manager_product_status_product_supplier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]