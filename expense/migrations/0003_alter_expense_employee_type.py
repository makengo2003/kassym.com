# Generated by Django 4.1.5 on 2023-12-25 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0002_expense_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='employee_type',
            field=models.CharField(choices=[('buyer', 'Закупщик/Сортировщик'), ('manager', 'Менеджер')], max_length=255),
        ),
    ]
