# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-23 16:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webparser', '0005_auto_20170423_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.1, max_digits=10, verbose_name='Цена'),
        ),
    ]
