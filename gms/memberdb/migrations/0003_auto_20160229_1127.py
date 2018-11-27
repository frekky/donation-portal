# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('memberdb', '0002_auto_20160229_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='membership_year',
            field=models.IntegerField(default=2016, verbose_name=b'Membership Year'),
            preserve_default=True,
        ),
    ]
