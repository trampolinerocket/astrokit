# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-26 18:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AstrometrySubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.IntegerField()),
                ('status', models.CharField(choices=[('SUBMITTED', 'Submitted'), ('COMPLETE', 'Complete'), ('FAILED_TO_SUBMIT', 'Failed to submit')], default='SUBMITTED', max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('succeeded_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='AstrometrySubmissionJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('SUCCESS', 'Success'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=50)),
                ('succeeded_at', models.DateTimeField()),
                ('annotations', jsonfield.fields.JSONField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='astrometry.AstrometrySubmission')),
            ],
        ),
    ]
