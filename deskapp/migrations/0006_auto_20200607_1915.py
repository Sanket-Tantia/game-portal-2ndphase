# Generated by Django 3.0.7 on 2020-06-07 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deskapp', '0005_auto_20200607_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='payout',
            field=models.IntegerField(blank=True, default=100, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='winx',
            field=models.IntegerField(blank=True, max_length=1, null=True),
        ),
    ]
