# Generated by Django 4.1.5 on 2023-10-24 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_product_code_lower'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='poster',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='products_images/'),
        ),
    ]