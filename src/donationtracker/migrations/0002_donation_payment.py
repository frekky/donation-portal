# Generated by Django 3.0.5 on 2020-05-02 05:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('squarepay', '0001_initial'),
        ('donationtracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='squarepay.CardPayment'),
        ),
    ]
