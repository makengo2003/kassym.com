# Generated by Django 4.1.5 on 2023-12-09 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0023_orderitem_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_same_with_last_order',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
