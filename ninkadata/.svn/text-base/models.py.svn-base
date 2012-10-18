from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Project(models.Model):
	name = models.CharField(max_length=250)
	version = models.CharField(max_length=100)
	distribution = models.CharField(max_length=100)
	def __unicode__(self):
		return self.name + " " + self.version

class License(models.Model):	
	name = models.CharField(max_length=250)

	def __unicode__(self):
		return self.name

class SourceFile(models.Model):
	name = models.CharField(max_length=250)
	directory = models.CharField(max_length=250)
	licenses = models.ManyToManyField(License)
	project = models.ForeignKey(Project)
	extension = models.CharField(max_length=20)
	goodsent_hash = models.CharField(max_length=300)
	def __unicode__(self):
		return self.name


class ProjectAdmin(admin.ModelAdmin):
	search_fields = ["name"]

class LicenseAdmin(admin.ModelAdmin):
	search_fields = ["name"]

class SourceFileAdmin(admin.ModelAdmin):
	search_fields = ["project"]

