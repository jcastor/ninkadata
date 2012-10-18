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
	file = SourceFile()
	try:
		currentproject = Project.objects.get(name=row[0],version=row[1],distribution="debian5")
	except Project.DoesNotExist:
		currentproject = Project()
		currentproject.name = row[0]
		currentproject.version = row[1]
		currentproject.distribution = "debian5"
		currentproject.save()
	file.project = currentproject
	lic = row[5].split(',')
	for license in lic:
		try:
			checklic = License.objects.get(name=license)
		except License.DoesNotExist:
			checklic = License()
			checklic.name = license
			checklic.save()
		file.save()
		file.licenses.add(checklic)
	file.name = row[4]
	file.directory = row[2]
	file.extension = row[3]
	file.goodsent_hash = row[6]
	file.save()
print "finished" + sys.argv[1]
f.close()
