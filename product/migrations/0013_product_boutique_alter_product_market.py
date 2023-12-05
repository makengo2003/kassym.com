# Generated by Django 4.1.5 on 2023-11-25 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_product_market'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='boutique',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='market',
            field=models.CharField(blank=True, choices=[('sadovod', 'Садовод'), ('yuzhnye_vorota', 'Южные ворота')], max_length=255, null=True),
        ),
    ]
