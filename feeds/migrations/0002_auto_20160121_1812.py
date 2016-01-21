# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-21 18:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0001_squashed_0007_auto_20160120_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='word',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=250, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='keyword',
            unique_together=set([('word', 'tag')]),
        ),
    ]