# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table('ninkadata_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('ninkadata', ['Project'])

        # Adding model 'License'
        db.create_table('ninkadata_license', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('ninkadata', ['License'])

        # Adding model 'SourceFile'
        db.create_table('ninkadata_sourcefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('directory', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ninkadata.Project'])),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('ninkadata', ['SourceFile'])

        # Adding M2M table for field licenses on 'SourceFile'
        db.create_table('ninkadata_sourcefile_licenses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sourcefile', models.ForeignKey(orm['ninkadata.sourcefile'], null=False)),
            ('license', models.ForeignKey(orm['ninkadata.license'], null=False))
        ))
        db.create_unique('ninkadata_sourcefile_licenses', ['sourcefile_id', 'license_id'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('ninkadata_project')

        # Deleting model 'License'
        db.delete_table('ninkadata_license')

        # Deleting model 'SourceFile'
        db.delete_table('ninkadata_sourcefile')

        # Removing M2M table for field licenses on 'SourceFile'
        db.delete_table('ninkadata_sourcefile_licenses')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ninkadata.License']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ninkadata.Project']"})
        }
    }

    complete_apps = ['ninkadata']