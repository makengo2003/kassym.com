# Generated by Django 4.1.5 on 2023-11-25 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_order_is_sorting_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'Новые'), ('accepted', 'Принятые'), ('is_sorting', 'В процессе'), ('sorted', 'Сортирован')], default='new', max_length=100),
        ),
    ]