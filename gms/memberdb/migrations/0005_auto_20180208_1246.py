# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('memberdb', '0004_auto_20170220_1840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='address',
        ),
        migrations.RemoveField(
            model_name='member',
            name='gender',
        ),
        migrations.AlterField(
            model_name='member',
            name='signed_up',
            field=models.DateField(default=datetime.date(2018, 2, 8), verbose_name=b'Signed up'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='member',
            name='student_no',
            field=models.CharField(max_length=20, verbose_name=b'Student Number or ID Number', blank=True),
            preserve_default=True,
        ),
    ]
