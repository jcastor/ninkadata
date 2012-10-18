django_project_home="/home/jcastor/django/myproject/"
import sys,os
sys.path.append(django_project_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from ninkadata.models import Project,License,SourceFile
import csv

csv_filepathname=sys.argv[1]
filepath2=sys.argv[2]
f = open(csv_filepathname)
f2 = open(filepath2)
dataReader = csv.reader(f, delimiter=';', quotechar='"')
dataReader2 = csv.reader(f2, delimiter=';', quotechar='"')
for row in dataReader:
	for rows in dataReader2:
		if row[2] == rows[2]:
			print row[0] + ';' + row[1] + ';' + row[2] + ';' + row[3] + ';' +rows[3]
f.close()
