# Generated by Django 4.1.5 on 2023-11-30 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0012_purchase_sorted_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='purchased_dt',
        ),
        migrations.AlterField(
            model_name='purchase',
            name='is_purchased_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='purchase.buyer'),
        ),
    ]
