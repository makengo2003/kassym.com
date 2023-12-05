# Generated by Django 4.1.5 on 2023-11-25 17:50

from django.db import migrations, models
import django.db.models.deletion
import purchase.models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0007_purchase_is_sorted'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='is_purchased_by',
            field=models.ForeignKey(default=purchase.models.get_main_buyer, on_delete=django.db.models.deletion.CASCADE, to='purchase.buyer'),
        ),
    ]