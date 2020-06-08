# Generated by Django 3.0.7 on 2020-06-07 11:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('deskapp', '0003_auto_20200607_1227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availabletoken',
            name='id',
        ),
        migrations.AlterField(
            model_name='availabletoken',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='available_token', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
