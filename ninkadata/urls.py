from django.conf.urls import patterns, include, url


urlpatterns = patterns('ninkadata.views',
	url(r'^project/(?P<pid>\d+)/files/(?P<page>\d+)/$', 'files'),
	url(r'^project/(?P<pid>\d+)/export/$', 'exportfile'),
	url(r'^distributions/$', 'distview'),
    url(r'^info/$', 'info'),
    url(r'^summary/$', 'summary'),
    url(r'^ninka/$', 'ninka'),
	url(r'^(?P<dist>\w+)/project/(?P<pid>\d+)/$', 'project'),
	url(r'^$', 'mainview'),
	url(r'^(?P<dist>\w+)/$', 'mainview'),
	url(r'^(?P<dist>\w+)/(?P<page>\d+)/(?P<rpp>\d+)/$', 'mainview'),
	url(r'^(?P<dist>\w+)/(?P<page>\d+)/$', 'mainview'),
)
