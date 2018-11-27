# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('memberdb', '0003_auto_20160229_1127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='membership_year',
        ),
        migrations.AlterField(
            model_name='member',
            name='email_address',
            field=models.CharField(max_length=200, verbose_name=b'Email Address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='member',
            name='phone_number',
            field=models.CharField(max_length=14, verbose_name=b'Phone Number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='member',
            name='signed_up',
            field=models.DateField(default=datetime.date(2017, 2, 20), verbose_name=b'Signed up'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='member',
            name='student_no',
            field=models.CharField(max_length=10, verbose_name=b'Student Number', blank=True),
            preserve_default=True,
        ),
    ]
