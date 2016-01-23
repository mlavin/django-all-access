# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import allaccess.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=255)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('access_token', allaccess.fields.EncryptedField(default=None, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('request_token_url', models.CharField(max_length=255, blank=True)),
                ('authorization_url', models.CharField(max_length=255)),
                ('access_token_url', models.CharField(max_length=255)),
                ('profile_url', models.CharField(max_length=255)),
                ('consumer_key', allaccess.fields.EncryptedField(default=None, null=True, blank=True)),
                ('consumer_secret', allaccess.fields.EncryptedField(default=None, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='accountaccess',
            name='provider',
            field=models.ForeignKey(to='allaccess.Provider', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountaccess',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='accountaccess',
            unique_together=set([('identifier', 'provider')]),
        ),
    ]
