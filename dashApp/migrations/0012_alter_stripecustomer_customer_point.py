# Generated by Django 3.2.16 on 2022-12-26 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashApp', '0011_auto_20221226_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripecustomer',
            name='customer_point',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
