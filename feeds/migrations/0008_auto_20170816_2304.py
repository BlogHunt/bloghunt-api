# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-16 23:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0007_auto_20170816_2304'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feed',
            old_name='rss_url',
            new_name='feed_url',
        ),
        migrations.AlterUniqueTogether(
            name='feed',
            unique_together=set([('site', 'feed_url')]),
        ),
    ]