# Generated by Django 4.1.5 on 2023-09-21 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_product_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='code_lower',
            field=models.CharField(blank=True, editable=False, max_length=500, null=True),
        ),
    ]
