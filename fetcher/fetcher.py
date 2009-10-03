import feedparser
import time
import urllib2
from lajfstrim.models import Feed, Item, Site
import settings
try:
    import json
except ImportError:
    import simplejson as json

print 'Checking and fetching feeds'
feeds = Feed.objects.all()
for feed in feeds:
    #print feed.link
    #print feed.link.startswith('http://blip.pl/')
    #try:
            fetched_feed = feedparser.parse(feed.link)
        #if feed.etag != fetched_feed['etag']:
            for feed_i in range(len(fetched_feed['entries'])):
                try:
                    Item.objects.get(user=feed.user.id, link = fetched_feed['entries'][feed_i]['link'])
                except:
                    try:
                        content = fetched_feed['entries'][feed_i].content[0].value
                    except:
                        content = fetched_feed['entries'][feed_i].get('summary',
                                     fetched_feed['entries'][feed_i].get('description', ''))
                    #try:
                    #    pubdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.mktime( time.strptime(fetched_feed['entries'][feed_i]['published'], "%Y-%m-%dT%H:%M:%SZ")))))
                    #except:
                    #    pubdate = fetched_feed['entries'][feed_i]['pubDate']
                    i = Item()
                    i.user_id = feed.user.id
                    i.type = 'feed'
                    i.title = fetched_feed['entries'][feed_i]['title']
                    i.link = fetched_feed['entries'][feed_i]['link']
                    i.date = time.strftime("%Y-%m-%d %H:%M:%S", fetched_feed['entries'][feed_i].updated_parsed)
                    i.body = content
                    i.save()
                    print fetched_feed['entries'][feed_i]['title']
            f = Feed.objects.get(id=feed.id)
            f.etag = fetched_feed['etag']
            f.save()
    #except:
    #    print 'We cant get feed %s' % feed.link
print 'Checking and fetching feeds - done'

print 'Checking and fetching site objects'
sites = Site.objects.all()
for site in sites:
    if site.site == 'blip':
        #http://api.blip.pl/users/kkszysiu/updates?limit=20&include=user,user[avatar]
        entries = json.loads(urllib2.urlopen(urllib2.Request('http://api.blip.pl/users/'+str(site.username)+'/statuses.json?limit=20&include=user,user[avatar],pictures')).read())
        for entry in entries:
            try:
                Item.objects.get(user=site.user.id, link = 'http://blip.pl/s/%s' % entry['id'])
            except:
                try:
                    picture = entry['pictures'][0]['url']
                    picture_mini = picture[0:-4]+'_inmsg.jpg'
                    picture_html = '<div class="user_picture"><a href="%s"><img src="%s"/></a></div>' % (picture, picture_mini)
                except:
                    picture_html = ''
                i = Item()
                i.user_id = site.user.id
                i.type = 'blip'
                i.title = None
                i.link = 'http://blip.pl/s/%s' % entry['id']
                i.date = entry['created_at']
                i.body = '<div class="content_image"><img src="http://blip.pl%s"/></div><span class="nickname">%s</span>: %s %s' % (entry['user']['avatar']['url_30'], entry['user']['login'], entry['body'], picture_html)
                i.save()
            #print entry['user']['login']
            #print entry['user']['avatar']['url_30']
            #print entry['body']
            #print entry['created_at']
    if site.site == 'twitter':
        try:
            statuses = json.loads(urllib2.urlopen(urllib2.Request('http://twitter.com/statuses/user_timeline.json?screen_name='+str(site.username)+'&count=20')).read())
            for status in statuses:
                try:
                    Item.objects.get(user=site.user, link = 'http://twitter.com/%s/status/%s/' % (site.username, status['id']))
                except:
                    i = Item()
                    i.user_id = site.user.id
                    i.type = 'twitter'
                    i.title = None
                    i.link = 'http://twitter.com/%s/status/%s/' % (site.username, status['id'])
                    i.date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.mktime(time.strptime(status['created_at'], "%a %b %d %H:%M:%S +0000 %Y")))))
                    i.body = '<div class="content_image"><img src="%s" width="32" height="32"/></div><span class="nickname">%s</span>: %s' % (status['user']['profile_image_url'], status['user']['screen_name'], status['text'])
                    i.save()
        except:
            print 'Cant fetch twitter tweets :('
    if site.site == 'identica':
        statuses = json.loads(urllib2.urlopen(urllib2.Request('http://identi.ca/api/statuses/user_timeline.json?screen_name='+str(site.username)+'&count=20')).read())
        for status in statuses:
            try:
                Item.objects.get(user=site.user, link = 'http://identi.ca/notice/%s' % status['id'])
            except:
                i = Item()
                i.user_id = site.user.id
                i.type = 'identica'
                i.title = None
                i.link = 'http://identi.ca/notice/%s' % status['id']
                i.date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.mktime(time.strptime(status['created_at'], "%a %b %d %H:%M:%S +0000 %Y")))))
                i.body = '<div class="content_image"><img src="%s" width="32" height="32"/></div><span class="nickname">%s</span>: %s' % (status['user']['profile_image_url'], status['user']['screen_name'], status['text'])
                i.save()
