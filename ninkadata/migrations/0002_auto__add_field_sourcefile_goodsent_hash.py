# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SourceFile.goodsent_hash'
        db.add_column('ninkadata_sourcefile', 'goodsent_hash',
                      self.gf('django.db.models.fields.CharField')(default='nohash', max_length=300),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SourceFile.goodsent_hash'
        db.delete_column('ninkadata_sourcefile', 'goodsent_hash')


    models = {
        'ninkadata.license': {
            'Meta': {'object_name': 'License'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'ninkadata.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ninkadata.sourcefile': {
            'Meta': {'object_name': 'SourceFile'},
            'directory': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'goodsent_hash': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ninkadata.License']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ninkadata.Project']"})
        }
    }

    complete_apps = ['ninkadata']