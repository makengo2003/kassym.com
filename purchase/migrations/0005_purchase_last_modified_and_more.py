# Generated by Django 4.1.5 on 2023-11-23 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_product_market'),
        ('purchase', '0004_alter_purchase_replaced_by_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='replaced_by_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
    ]
