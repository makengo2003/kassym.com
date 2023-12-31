# Generated by Django 4.1.5 on 2023-08-11 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0002_alter_contact_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='type',
            field=models.CharField(choices=[('phone_number', 'Номер телефона'), ('whatsapp', 'Whatsapp'), ('email', 'Эл. почта'), ('instagram', 'Instagram'), ('order_manager', 'Номер менеджера по заказам'), ('footer', 'Footer'), ('telegram_chat_id', 'Ваш Chat Id в Telegram')], max_length=100, unique=True),
        ),
    ]
