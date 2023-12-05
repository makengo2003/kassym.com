from django.db import migrations, models
import project.utils


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_userrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrequest',
            name='created_at',
            field=models.DateField(default=project.utils.datetime_now, editable=False),
        ),
    ]
