# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-26 19:22
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('astrometry', '0006_astrometrysubmissionjob_jobid'),
    ]

    operations = [
        migrations.AddField(
            model_name='astrometrysubmissionjob',
            name='info',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]