# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from ..compat import get_user_model, AUTH_USER_MODEL

User = get_user_model()


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Provider.authorization_url'
        db.alter_column('allaccess_provider', 'authorization_url', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Provider.profile_url'
        db.alter_column('allaccess_provider', 'profile_url', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Provider.request_token_url'
        db.alter_column('allaccess_provider', 'request_token_url', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Provider.access_token_url'
        db.alter_column('allaccess_provider', 'access_token_url', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'Provider.authorization_url'
        db.alter_column('allaccess_provider', 'authorization_url', self.gf('django.db.models.fields.URLField')(max_length=200))

        # Changing field 'Provider.profile_url'
        db.alter_column('allaccess_provider', 'profile_url', self.gf('django.db.models.fields.URLField')(max_length=200))

        # Changing field 'Provider.request_token_url'
        db.alter_column('allaccess_provider', 'request_token_url', self.gf('django.db.models.fields.URLField')(max_length=200))

        # Changing field 'Provider.access_token_url'
        db.alter_column('allaccess_provider', 'access_token_url', self.gf('django.db.models.fields.URLField')(max_length=200))

    models = {
        'allaccess.accountaccess': {
            'Meta': {'unique_together': "(('identifier', 'provider'),)", 'object_name': 'AccountAccess'},
            'access_token': ('allaccess.fields.EncryptedField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['allaccess.Provider']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['%s']" % AUTH_USER_MODEL, 'null': 'True', 'blank': 'True'})
        },
        'allaccess.provider': {
            'Meta': {'object_name': 'Provider'},
            'access_token_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'authorization_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'consumer_key': ('allaccess.fields.EncryptedField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'consumer_secret': ('allaccess.fields.EncryptedField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'request_token_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        AUTH_USER_MODEL: {
            'Meta': {'object_name': User.__name__, "db_table": "'%s'" % User._meta.db_table},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['allaccess']