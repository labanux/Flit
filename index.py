"""
Percobaan bikin apps pake Flask, buat nyari Link apa yang lagi populer di Twitter.
"""

from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from fetch_url import get_summary
import datetime
import hashlib
import pycurl
import StringIO
import json
from pymongo import Connection, ASCENDING, DESCENDING

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    flit = Connection().flit        
    links = flit.links
    #links = flit.linkspic
    
    # Ambil data dari 2 jam yang lalu
    d = datetime.datetime.now() - datetime.timedelta(hours=2)
        
    items = links.find({'created' : {"$gt" : d}}).sort([('count', DESCENDING), ('created', DESCENDING)]).limit(10)
    
    return render_template('index.html', items = items)

@app.route('/scan')
def scan():
    cities = {
        'jakarta' : '-6.2%2C106.8',
        'bandung' : '-6.914744%2C07.609811',
        'semarang' : '-6.966667%2C110.416667',
        'yogyakarta' : '-7.801389%2C110.364444',
        'malang' : '-7.98%2C112.62',
        'surabaya' : '-7.265278%2C112.7425',
        'bali' : '-8.65%2C115.216667',        
        'medan' : '3.583333%2C98.666667',
        'pekanbaru' : '0.533333%2C101.45',
        'palembang' : '-2.991108%2C104.756733',
        'padang' : '-0.95%2C100.353056',
        'makassar' : '-5.133333%2C119.416667',
        'manado' : '1.493056%2C124.841261'
    }
    
    city = cities['jakarta']
    
    twitter_search = 'http://search.twitter.com/search.json?q=http+filter:links+-Like+-mtw.tl+-4sq.com+-tmi.me+-myloc.me+-tl.gd+include%3Aretweets&geocode='+city+'%2C100km'
    #twitter_search = 'http://search.twitter.com/search.json?q=http+twitpic+filter:links+include%3Aretweets&geocode='+city+'%2C100km'
    conn = pycurl.Curl()
    b = StringIO.StringIO()
    
    conn.setopt(pycurl.URL, twitter_search)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform() 

    data = b.getvalue()
    data = json.loads(data)
    
    flit = Connection().flit    
    twits = flit.twits
    links = flit.links
    
    #twits = flit.twitspic
    #links = flit.linkspic
    
    for i in data['results'] :        
        recorded_twits = twits.find({'twit_id' : i['id']})
        #print 'Checking Twit ID ', i['id']
        #print 'Recorded twits', recorded_twits.count()
        
        if recorded_twits.count() < 1 :
            #print 'Twit ini belum disimpan ', i['text']
            
            twit = {
                'text' : i['text'],
                'username' : i['from_user'],
                'created' : datetime.datetime.utcnow(),
                'twit_id' : i['id']
            }
            twits.insert(twit)
            
            import re
            link_url = re.search("(?P<url>https?://[^\s]+)", i['text']).group("url")
            
            import urllib2
            try:
                response = urllib2.urlopen(link_url)
                link_url = response.url
            except IOError, e:                
                continue
            
            hashed_url = hashlib.sha1(link_url).hexdigest()
            recorded_links = links.find({'hashed_url' : hashed_url})
            
            if recorded_links.count() == 0 :
                #print 'Link ini belum disimpan : ', link_url
                #content = url_description(link_url)
                #content = content['result']
                (title, desc) = get_summary(link_url)
                
                domain = link_url.split('/', 3)[2]
                
                link = {
                    'title' : title,
                    'description' : desc,
                    'url' : link_url,
                    'domain' : domain,
                    'username' : i['from_user'],
                    'count' : 0,
                    'created' : datetime.datetime.now(),                    
                    'hashed_url' : hashed_url
                }
                
                links.insert(link)
                #print 'Save ', i['id']
            else :
                #print 'Link ini sudah pernah disimpan, update saja ', link_url
                links.update({'_id' : recorded_links[0]['_id']}, {'$set': {'count': recorded_links[0]['count'] + 1}})
                #count' : (recorded_links[0]['count'] + 1)}
        #else :
            #print 'Twit ini sudah pernah diproses. Skip ', i['text']
    
    return render_template('scan.html', data = 'done')
    
def scan_cmd() :
    cities = {
        'jakarta' : '-6.2%2C106.8',
        'bandung' : '-6.914744%2C07.609811',
        'semarang' : '-6.966667%2C110.416667',
        'yogyakarta' : '-7.801389%2C110.364444',
        'malang' : '-7.98%2C112.62',
        'surabaya' : '-7.265278%2C112.7425',
        'bali' : '-8.65%2C115.216667',        
        'medan' : '3.583333%2C98.666667',
        'pekanbaru' : '0.533333%2C101.45',
        'palembang' : '-2.991108%2C104.756733',
        'padang' : '-0.95%2C100.353056',
        'makassar' : '-5.133333%2C119.416667',
        'manado' : '1.493056%2C124.841261'
    }
    
    city = cities['jakarta']
    
    twitter_search = 'http://search.twitter.com/search.json?q=http+filter:links+-Like+-mtw.tl+-4sq.com+-tmi.me+-myloc.me+-tl.gd+include%3Aretweets&geocode='+city+'%2C100km'
    #twitter_search = 'http://search.twitter.com/search.json?q=http+twitpic+filter:links+include%3Aretweets&geocode='+city+'%2C100km'
    conn = pycurl.Curl()
    b = StringIO.StringIO()
    
    conn.setopt(pycurl.URL, twitter_search)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform() 

    data = b.getvalue()
    data = json.loads(data)
    
    flit = pymongo.Connection().flit    
    twits = flit.twits
    links = flit.links
    
    #twits = flit.twitspic
    #links = flit.linkspic
    
    for i in data['results'] :        
        recorded_twits = twits.find({'twit_id' : i['id']})
        #print 'Checking Twit ID ', i['id']
        #print 'Recorded twits', recorded_twits.count()
        
        if recorded_twits.count() < 1 :
            #print 'Twit ini belum disimpan ', i['text']
            
            twit = {
                'text' : i['text'],
                'username' : i['from_user'],
                'created' : datetime.datetime.utcnow(),
                'twit_id' : i['id']
            }
            twits.insert(twit)
            
            import re
            link_url = re.search("(?P<url>https?://[^\s]+)", i['text']).group("url")
            
            import urllib2
            try:
                response = urllib2.urlopen(link_url)
                link_url = response.url
            except IOError, e:                
                continue
            
            hashed_url = hashlib.sha1(link_url).hexdigest()
            recorded_links = links.find({'hashed_url' : hashed_url})
            
            if recorded_links.count() == 0 :
                #print 'Link ini belum disimpan : ', link_url
                #content = url_description(link_url)
                #content = content['result']
                (title, desc) = get_summary(link_url)
                
                domain = link_url.split('/', 3)[2]
                
                link = {
                    'title' : title,
                    'description' : desc,
                    'url' : link_url,
                    'domain' : domain,
                    'username' : i['from_user'],
                    'count' : 0,
                    'created' : datetime.datetime.now(),                    
                    'hashed_url' : hashed_url
                }
                
                links.insert(link)
                #print 'Save ', i['id']
            else :
                #print 'Link ini sudah pernah disimpan, update saja ', link_url
                links.update({'_id' : recorded_links[0]['_id']}, {'$set': {'count': recorded_links[0]['count'] + 1}})
                #count' : (recorded_links[0]['count'] + 1)}
        #else :
            #print 'Twit ini sudah pernah diproses. Skip ', i['text']
    
    print 'sudah...'
    
if __name__ == '__main__':
    app.run()
    
