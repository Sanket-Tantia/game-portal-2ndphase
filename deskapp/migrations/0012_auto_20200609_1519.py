# Generated by Django 3.0.7 on 2020-06-09 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deskapp', '0011_auto_20200608_1611'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='payout',
            new_name='probability',
        ),
    ]
