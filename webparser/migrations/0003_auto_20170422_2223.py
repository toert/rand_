# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-22 19:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webparser', '0002_auto_20170422_1909'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ad',
            options={'verbose_name': 'Объявление', 'verbose_name_plural': 'Мои объявления'},
        ),
    ]