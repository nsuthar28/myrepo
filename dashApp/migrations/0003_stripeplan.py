# Generated by Django 3.2.16 on 2022-12-13 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashApp', '0002_stripecustomer_is_subscribed'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
                ('price_id', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('expired_date', models.DateTimeField()),
                ('trial_start', models.DateTimeField()),
                ('trial_end', models.DateTimeField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashApp.stripecustomer')),
            ],
        ),
    ]
