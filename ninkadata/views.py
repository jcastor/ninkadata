from django.shortcuts import render_to_response
from ninkadata.models import *
from ninkadata.forms import *
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.core.context_processors import csrf
import subprocess
import tarfile
import csv
import hashlib
from django.http import HttpResponse
# View: mainview
# This view is the view that shows the project listing for the site, depending on the distribution in "dist"
# Pagination is handled by the "page" variable, and the results per page are handled by "rpp".  Queries are 
# handled with a GET request, and are used with a regex.
def mainview(request,dist="debian4",page="1",rpp="25"):
	query = request.GET.get('q', '')
	if query:
		if dist == "all":
			qset = (Q(name__iregex=query))
			results = Project.objects.filter(qset).distinct()
		else:
			qset = (Q(name__iregex=query))
			results = Project.objects.filter(qset, distribution=dist).distinct()

	else:
		results = []
	if dist == "all":
		projects = 	Project.objects.all().order_by("name").distinct('name')
		paginator = Paginator(projects, int(rpp))
		
	else:
		projects = 	Project.objects.filter(distribution=dist).order_by("name").distinct('name')
		paginator = Paginator(projects, int(rpp))
	try:
		dist = Project.objects.filter(distribution=dist)[0]
	except IndexError:
		dist = Project.objects.all()
	try: page = int(page)
	except ValueError: page = 1

	try:
		projects = paginator.page(page)
	except (InvalidPage, EmptyPage):
		projects = paginator.page(paginator.num_pages)
	p = dict(rpp=rpp,projects=projects,query=query,results=results,dist=dist,user=request.user)
	return render_to_response("projects.html", p)
# View: distview
# This view shows a listing of the unique distributions so that this can be displayed on the first entry page
def distview(request):
	from django.db import connection, transaction
	cursor = connection.cursor()
#	cursor.execute('SELECT distribution,projcount,namecount FROM (select distribution,count(ninkadata_project.name) as projcount from ninkadata_project group by distribution) as foo1 NATURAL JOIN (select distribution,count(ninkadata_sourcefile.id) as namecount from ninkadata_project INNER JOIN ninkadata_sourcefile ON (ninkadata_project.id=ninkadata_sourcefile.project_id) GROUP BY distribution) as foo2 ORDER BY projcount DESC')
	cursor.execute('SELECT * FROM matdistview') #created a materialized view in order to improve performance rather than using the rather long query above
	dists = cursor.fetchall()
	allcount = 0
	allsourcecount = 0
	for distribution,projcount,namecount in dists: #much better for performance to manually calculate the counts for all by using the data from the materialized view, if you had many distributions, it would not be very good though
		allcount = allcount + projcount
		allsourcecount = allsourcecount + namecount
#	allcount = Project.objects.all().count()
#	allsourcecount = SourceFile.objects.all().count()
	p = dict(dists=dists,allcount=allcount,allsourcecount=allsourcecount)
	return render_to_response("dist.html",p)
# View: summary
# Displays some generic summary information, most popular licenses, etc
def summary(request):
	projects = Project.objects.all().annotate(count=Count('sourcefile__name')).order_by('-count')
	projects = projects[0:10]
	poplicense = License.objects.all().annotate(count=Count('sourcefile__name')).order_by('-count')
	poplicense = poplicense[0:10]
	p = dict(poplicense=poplicense,projects=projects)
	return render_to_response("summary.html",p)
# View: project
# This view displays a list of projects that match the name given by the project with id = pid.  This allows us
# to display all versions of a project within the same distribution
def project(request, pid, dist="debian4"):
	project = Project.objects.get(id=int(pid))
	if dist == "all":
		projectWithName = Project.objects.filter(name=project.name).annotate(count=Count('sourcefile'))
	else:
		projectWithName = Project.objects.filter(name=project.name,distribution=dist).annotate(count=Count('sourcefile'))
	pr = dict(projectWithName=projectWithName, project=project)
	return render_to_response("project.html",pr)
# View: info
# Just displays a generic info template
def info(request):
	return render_to_response("info.html")
# View: ninka
# This view allows users to use the ninka program on either individual files or on .tar.gz archives
# If the file is an archive it is saved into tmp.tar.gz, then extracted and has a subprocess of ninka run on
# each file that was extracted
def ninka(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		results = {}
		if form.is_valid():
			filename = request.FILES['file'].name
			if ".tar.gz" in filename:
				handle_file(request.FILES['file'],'.tar.gz')
				var = "/var/www/media/tmp/files/tmp.tar.gz" #where to save the file temporarily 
				tar = tarfile.open(var,"r:gz")
				tar.extractall("/var/www/media/tmp/files/") #location to extract the files
				for tarinfo in tar:
					if tarinfo.isdir():
						pass #do nothing if it is a directory
					else: #otherwise run ninka on each file
						filename = "/var/www/media/tmp/files/" + tarinfo.name
						pipe = subprocess.Popen(["perl", "/var/www/media/tmp/ninka/ninka.pl", filename], stdout=subprocess.PIPE)
						result = pipe.stdout.read()
						md5 = md5Checksum("/var/www/media/tmp/files/" + tarinfo.name + ".goodsent")
						results[tarinfo.name] = result + " " + md5
				result = ""
				tar.close
			else:
				handle_file(request.FILES['file'], '.txt')
				var = "/var/www/media/tmp/files/tmp.txt"
				pipe = subprocess.Popen(["perl", "/var/www/media/tmp/ninka/ninka.pl", var], stdout=subprocess.PIPE)
				result = pipe.stdout.read()
				results[filename] = result
			pr = dict(results=results, filename=filename)
			return render_to_response("ninka.html",pr)
	else:
		form = UploadFileForm()
	p = dict(form=form)
	return render_to_response("ninka.html", p, context_instance=RequestContext(request))

# View: files
# This view shows the files within a project, based on the project id given in "pid". Pagination
# is handled by the "page" variable, rather than through a GET request.  This also handles filtering
# depending by the get variables filterd and hashed, the results are filtered.
def files(request, pid, page):
	from django.db import connection, transaction
	cursor = connection.cursor()
	filterd = request.GET.getlist('licenses')
	hashed = request.GET.getlist('hash')
	projects = Project.objects.get(id=int(pid))
	cursor.execute('SELECT goodsent_hash, count(goodsent_hash) as count FROM ninkadata_sourcefile WHERE project_id = %s GROUP BY goodsent_hash ORDER BY count DESC', [projects.id])
	hashes = cursor.fetchall()
	if filterd:
		files = SourceFile.objects.filter(licenses__in=filterd, project=projects)
		filecount = SourceFile.objects.filter(licenses__in=filterd,project = projects).count()
	elif hashed:
		files = SourceFile.objects.filter(goodsent_hash__in=hashed, project=projects)
		filecount = SourceFile.objects.filter(goodsent_hash__in=hashed,project=projects).count()
	else:
		files = SourceFile.objects.filter(project = projects)
		filecount = SourceFile.objects.filter(project = projects).count()
		paginator = Paginator(files, 50)
		try:
			files = paginator.page(page)
		except (InvalidPage, EmptyPage):
			files = paginator.page(paginator.num_pages)
		try: page = int(page)
		except ValueError: page = 1

	ccount = SourceFile.objects.filter(extension = ".c", project=projects).count()
	cppcount = SourceFile.objects.filter(extension = ".cpp", project=projects).count()
	javacount = SourceFile.objects.filter(extension = ".java", project=projects).count()
	plcount = SourceFile.objects.filter(extension = ".pl", project=projects).count()
	pycount = SourceFile.objects.filter(extension = ".py", project=projects).count()
	hcount = SourceFile.objects.filter(extension = ".h", project=projects).count()
	othercount = SourceFile.objects.filter(project=projects).count() - (ccount + cppcount + javacount + plcount + pycount + hcount)
	liccount = License.objects.filter(sourcefile__in=SourceFile.objects.filter(project=projects)).annotate(count=Count('sourcefile'))
	
	fr = dict(hashes=hashes,filterd=filterd,files=files, projects=projects,filecount=filecount,ccount=ccount,javacount=javacount,cppcount=cppcount,plcount=plcount,pycount=pycount,hcount=hcount,othercount=othercount,liccount=liccount, user=request.user)
	return render_to_response("files.html",fr,context_instance=RequestContext(request))

# View: exportfile
# This view exports a text file with the data for a project
def exportfile(request,pid):
	projects = Project.objects.get(id=int(pid))
	files = SourceFile.objects.filter(project=projects)
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=' + projects.name + '.txt'

	writer = csv.writer(response)
	writer.writerow(['## Package Information'])
	writer.writerow(['PackageName: ' + projects.name])
	writer.writerow(['PackageVersion: ' + projects.version])
	writer.writerow(['PackageDistribution: ' + projects.distribution])
	writer.writerow(['---'])
	writer.writerow(['## File Information'])
	for f in files:
		writer.writerow(['FileName: ' + f.directory])
		writer.writerow(['FileType: ' + f.extension])
		writer.writerow(['.goodsent hash: MD5: ' + f.goodsent_hash])
		for l in f.licenses.all():
			writer.writerow(['LicenseConcluded: ' + str(l)])
		writer.writerow(['---'])
		
	return response


# Function: handle_file
# This function is used by the ninka view and writes the file to the temporary directory
def handle_file(f, filetype):
	with open('/var/www/media/tmp/files/tmp' + filetype, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
# Function md5Checksum
# This function is used to calculate hashes
def md5Checksum(filePath):
        fh = open(filePath, 'rb')
        m=hashlib.md5()
        while True:
                data = fh.read(8192)
                if not data:
                        break
                m.update(data)
        return m.hexdigest()