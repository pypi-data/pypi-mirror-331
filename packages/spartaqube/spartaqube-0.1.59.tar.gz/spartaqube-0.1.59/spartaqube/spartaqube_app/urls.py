from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_cbfa5749ed.sparta_46362b862f.qube_0c99e82f57.sparta_0c81d6de1d'
handler500='project.sparta_cbfa5749ed.sparta_46362b862f.qube_0c99e82f57.sparta_5e61ef1855'
handler403='project.sparta_cbfa5749ed.sparta_46362b862f.qube_0c99e82f57.sparta_321c7b16d9'
handler400='project.sparta_cbfa5749ed.sparta_46362b862f.qube_0c99e82f57.sparta_edb26225bc'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]