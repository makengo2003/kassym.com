# Generated by Django 4.1.5 on 2023-12-05 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('purchase', '0015_remove_purchase_sorted_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='buyer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='is_purchased_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='purchase.buyer'),
        ),
    ]
