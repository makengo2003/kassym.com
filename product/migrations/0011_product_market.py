# Generated by Django 4.1.5 on 2023-11-21 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_alter_product_poster'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='market',
            field=models.CharField(blank=True, choices=[('sadovod', 'Sadovod'), ('yuzhnoe', 'Yuzhnoe')], max_length=255, null=True),
        ),
    ]
