# Generated by Django 3.0.5 on 2020-05-02 05:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Account name')),
                ('balance_cents', models.IntegerField(default=0, verbose_name='Account balance in cents')),
                ('is_charitable', models.BooleanField(default=False, verbose_name='Can be recipient of donations')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_cents', models.IntegerField(verbose_name='Donation amount')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('acct_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='donations_from_me', to='donationtracker.BalanceAccount')),
                ('acct_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='donations_to_me', to='donationtracker.BalanceAccount')),
            ],
        ),
    ]
