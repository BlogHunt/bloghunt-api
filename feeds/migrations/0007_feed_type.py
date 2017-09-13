# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-11 06:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0006_auto_20170907_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='type',
            field=models.CharField(choices=[('RSS Feed', 'rss'), ('JSON Feed', 'jsonfeed')], default='rss', max_length=10),
        ),
    ]
