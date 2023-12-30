# Generated by Django 4.1.5 on 2023-12-30 01:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('product_status', 'Остатки'), ('order_status', 'Мои заказы'), ('news', 'Новости'), ('tech_support', 'Тех. поддержка')], max_length=255)),
                ('text', models.TextField()),
                ('dt', models.DateTimeField()),
                ('has_read', models.BooleanField(default=False)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages_from_me', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages_to_me', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]