# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-16 23:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import feeds.models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0008_auto_20170816_2304'),
    ]

    operations = [
        migrations.RunPython(
            create_sites_from_feed
        ),
        migrations.AlterField(
            model_name='feed',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feeds', to='feeds.Site'),
        ),
    ]
