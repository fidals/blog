# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-18 16:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0005_auto_20170317_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='object_id',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
