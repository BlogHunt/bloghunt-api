# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-21 23:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0012_site_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]