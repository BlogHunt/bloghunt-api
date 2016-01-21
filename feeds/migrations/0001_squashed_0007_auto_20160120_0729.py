# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-21 02:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [
        ('feeds', '0001_initial'), ('feeds', '0002_auto_20160118_2113'), ('feeds', '0003_feed_last_updated'),
        ('feeds', '0004_auto_20160119_0122'), ('feeds', '0005_auto_20160119_0134'),
        ('feeds', '0006_auto_20160120_0716'), ('feeds', '0007_auto_20160120_0729'),
    ]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rss_url', models.URLField(unique=True, verbose_name='RSS URL')),
                ('title', models.CharField(blank=True, max_length=250, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(editable=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('word', models.CharField(blank=True, max_length=250, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(default='', max_length=250, unique=True)),
                ('slug', models.SlugField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='keyword',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feeds.Tag'),
        ),
        migrations.AddField(
            model_name='feed',
            name='tags',
            field=models.ManyToManyField(to='feeds.Tag'),
        ),
    ]