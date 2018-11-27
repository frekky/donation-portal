# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('real_name', models.CharField(max_length=200, verbose_name=b'Real Name')),
                ('username', models.CharField(max_length=16, verbose_name=b'Username', blank=True)),
                ('address', models.TextField(verbose_name=b'Postal Address', blank=True)),
                ('membership_type', models.IntegerField(verbose_name=b'Membership Type', choices=[(1, b"O' Day Special"), (2, b'Student'), (3, b'Non Student')])),
                ('guild_member', models.BooleanField(default=False, verbose_name=b'Guild Member')),
                ('phone_number', models.CharField(default=False, max_length=14, verbose_name=b'Phone Number', blank=True)),
                ('email_address', models.CharField(default=False, max_length=200, verbose_name=b'Email Address', blank=True)),
                ('student_no', models.CharField(default=False, max_length=10, verbose_name=b'Student Number', blank=True)),
                ('date_of_birth', models.DateField(null=True, verbose_name=b'Date of Birth', blank=True)),
                ('gender', models.IntegerField(default=1, verbose_name=b'Gender', choices=[(1, b'Male'), (2, b'Female'), (3, b'Other'), (4, b'Undefined')])),
                ('signed_up', models.DateField(default=datetime.date(2015, 2, 20), verbose_name=b'Signed up')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
