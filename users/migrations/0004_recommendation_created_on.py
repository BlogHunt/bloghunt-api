# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-31 00:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170829_0037'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendation',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]