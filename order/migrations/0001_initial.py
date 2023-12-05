# Generated by Django 4.1.5 on 2023-12-05 22:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import project.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0014_merge_20231205_2221'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manager', '0002_alter_manager_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=project.utils.datetime_now, editable=False)),
                ('status', models.CharField(blank=True, choices=[('new', 'В обработке'), ('accepted', 'Принят'), ('is_sorting', 'Сортируется'), ('sorted', 'Сортирован'), ('delivered', 'Отправлен')], default='new', max_length=100)),
                ('company_name', models.CharField(max_length=255, null=True)),
                ('deliveries_qr_code', models.FileField(upload_to='deliveries_qr_code/')),
                ('selection_sheet_file', models.FileField(upload_to='selection_sheet_files/')),
                ('is_express', models.BooleanField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('paid_check_file', models.FileField(upload_to='paid_check_files/')),
                ('ruble_rate', models.FloatField()),
                ('total_products_price', models.PositiveIntegerField()),
                ('total_sum_in_tenge', models.FloatField()),
                ('total_sum_in_ruble', models.PositiveIntegerField()),
                ('total_products_count', models.PositiveIntegerField()),
                ('service_price_per_count', models.PositiveIntegerField()),
                ('express_price_per_count', models.PositiveIntegerField()),
                ('total_service_price', models.PositiveIntegerField()),
                ('specific_product', models.BooleanField()),
                ('price_for_specific_product', models.PositiveIntegerField()),
                ('is_sorting_by', models.CharField(blank=True, max_length=500, null=True)),
                ('delivered_by', models.CharField(blank=True, max_length=500, null=True)),
                ('sorted_dt', models.DateTimeField(blank=True, null=True)),
                ('accepted_dt', models.DateTimeField(blank=True, null=True)),
                ('delivered_dt', models.DateTimeField(blank=True, null=True)),
                ('sorted_report', models.ImageField(blank=True, null=True, upload_to='order_is_sorted_reports/')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='manager.manager')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField()),
                ('qr_code', models.FileField(upload_to='products_qr_code/')),
                ('product_price', models.PositiveIntegerField()),
                ('total_price', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.product')),
            ],
        ),
    ]
