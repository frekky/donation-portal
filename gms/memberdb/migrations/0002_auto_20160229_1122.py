# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('memberdb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='membership_year',
            field=models.IntegerField(default=2017, verbose_name=b'Membership Year'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='member',
            name='signed_up',
            field=models.DateField(default=datetime.date(2016, 2, 26), verbose_name=b'Signed up'),
            preserve_default=True,
        ),
    ]
