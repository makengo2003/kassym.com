# Generated by Django 4.1.5 on 2023-12-11 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0026_order_canceled_dt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'В обработке'), ('accepted', 'Принят'), ('is_sorting', 'Сортируется'), ('sorted', 'Сортирован'), ('delivered', 'Отправлен'), ('canceled', 'Отменен')], default='new', max_length=100),
        ),
    ]