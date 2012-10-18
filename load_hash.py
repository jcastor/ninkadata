django_project_home="/home/jcastor/django/myproject/"
import sys,os
sys.path.append(django_project_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from ninkadata.models import Project,License,SourceFile
import csv

csv_filepathname=sys.argv[1]
f = open(csv_filepathname)
dataReader = csv.reader(f, delimiter=';', quotechar='"')
for row in dataReader:
	try:
		SourceFile.objects.filter(directory = row[2]).update(goodsent_hash=row[6])
	except SourceFile.DoesNotExist:
		pass
f.close()
