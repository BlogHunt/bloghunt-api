# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-07-28 21:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feeds', '0004_feed_cached_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_feeds', to=settings.AUTH_USER_MODEL),
        ),
    ]
