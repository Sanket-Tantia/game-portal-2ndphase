# Generated by Django 3.0.7 on 2020-06-07 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deskapp', '0007_auto_20200607_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='payout',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
