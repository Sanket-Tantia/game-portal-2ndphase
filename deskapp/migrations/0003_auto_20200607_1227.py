# Generated by Django 3.0.7 on 2020-06-07 06:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('deskapp', '0002_retailermapping'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'default_related_name': 'profile'},
        ),
        migrations.AlterModelOptions(
            name='retailermapping',
            options={'default_related_name': 'retailer_mapping'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='TransactionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_amount', models.IntegerField()),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('issuer_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='issuer', to=settings.AUTH_USER_MODEL)),
                ('receiver_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiver', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'transaction_log',
            },
        ),
        migrations.CreateModel(
            name='AvailableToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_amount', models.IntegerField()),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='available_token', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'available_token',
            },
        ),
    ]