# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-22 21:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0013_site_created_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, max_length=250, null=True)),
                ('identifier', models.CharField(choices=[('HTTPError', 'HTTP Error'), ('MissingOrInvalidSchemaError', 'Missing or Invalid Schema Error'), ('ConnectionError', 'Connection Error'), ('NotAFeedError', 'Not A Feed Error'), ('NotAnRSSFeedError', 'Not An RSS Feed Error'), ('SiteHasNoFeedsError', 'Site Has No Feeds Error')], max_length=50)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='feed',
            name='error',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feed', to='feeds.Error'),
        ),
        migrations.AddField(
            model_name='site',
            name='error',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='site', to='feeds.Error'),
        ),
    ]
