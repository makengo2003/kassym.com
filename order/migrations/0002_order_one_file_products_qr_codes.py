# Generated by Django 4.1.5 on 2023-11-07 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='one_file_products_qr_codes',
            field=models.FileField(null=True, upload_to='one_file_products_qr_codes/'),
        ),
    ]