# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-05 10:03
from __future__ import unicode_literals

import account.utilities
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0006_auto_20170705_0952'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=account.utilities.generate_security_token, max_length=64)),
                ('expiry_date', models.DateTimeField(default=account.utilities.days_from_current_time)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
