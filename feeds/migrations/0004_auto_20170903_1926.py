# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-03 19:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0003_auto_20170903_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
