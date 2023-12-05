# Generated by Django 4.1.5 on 2023-11-23 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_delete_orderitempurchase'),
        ('product', '0012_alter_product_market'),
        ('purchase', '0002_alter_buyer_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'В обработке'), ('purchased', 'Куплен'), ('not_available', 'Нет в наличий'), ('will_be_tomorrow', 'Будет завтра'), ('replaced', 'Заменён')], default='new', max_length=50)),
                ('price_per_count', models.PositiveIntegerField(default=0)),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='order.orderitem')),
                ('replaced_by_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
    ]
