# Generated by Django 3.2.16 on 2022-12-14 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashApp', '0006_stripecustomer_stripeproductid'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripecustomer',
            name='subscription_end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='stripecustomer',
            name='trial_end',
            field=models.DateTimeField(null=True),
        ),
    ]