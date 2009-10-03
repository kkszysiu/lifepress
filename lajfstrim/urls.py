import os
from django.conf.urls.defaults import *
import django.contrib.auth.views

urlpatterns = patterns('',
    (r'^login/$', 'lajfstrim.views.login_user'),
    (r'^registration/$', 'lajfstrim.views.register'),
    #(r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    
    (r'^accounts/profile/$', 'lajfstrim.views.smart_redirect'),

    url(r'^user/(?P<user>\w+)/$', 'lajfstrim.views.user_mainsite', name='user_mainsite'),
    url(r'^user/(?P<user>\w+)/(?P<section_view>list|my|friends)/$', 'lajfstrim.views.user_mainsite', name='user_mainsite'),
    #better if timeline will be other fuction for reasion of diference and complexity
    url(r'^user/(?P<user>\w+)/timeline/$', 'lajfstrim.views.user_mainsite_timeline', name='user_mainsite_timeline'),
    url(r'^user/(?P<user>\w+)/add_friend/$', 'lajfstrim.views.add_friend', name='add_friend'),
    url(r'^user/(?P<user>\w+)/(?P<id>\d+)/$', 'lajfstrim.views.show_id', name='show_id'),


    url(r'^user_panel/$', 'lajfstrim.views.user_admin', name='user_admin'),
    url(r'^user_panel/user/$', 'lajfstrim.views.user_admin_user', name='user_admin_user'),
    url(r'^user_panel/add_feed/$', 'lajfstrim.views.user_admin_feed', name='user_admin_feed'),
    url(r'^user_panel/edit_feed/(?P<id>\d+)/$', 'lajfstrim.views.user_admin_feed', name='user_admin_feed'),
    url(r'^user_panel/add_site/$', 'lajfstrim.views.user_admin_site', name='user_admin_site'),
    url(r'^user_panel/edit_site/(?P<id>\d+)/$', 'lajfstrim.views.user_admin_site', name='user_admin_site'),
    url(r'^user_panel/(?P<type>site|feed)s/$', 'lajfstrim.views.user_admin_site_feed_management', name='user_admin_site_feed_management'),
    url(r'^$', 'lajfstrim.views.index', name='planet_index'),
    
    
)
