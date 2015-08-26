# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('allaccess', '0002_auto_20150511_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='site',
            field=models.ForeignKey(default=None, blank=True, to='sites.Site', null=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='provider',
            unique_together=set([('name', 'site')]),
        ),
    ]
