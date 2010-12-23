"""
Percobaan bikin apps pake Flask, buat nyari Link apa yang lagi populer di Twitter. *coba kasih editan aja deh :)
"""

from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
import datetime
import hashlib
import pycurl
import StringIO
import json
from pymongo import Connection

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
#app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

@app.route('/')
def index():
    return "hello"

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
    
    for i in data['results'] :        
        recorded_twits = twits.find({'twit_id' : i['id']})
        print 'Checking Twit ID ', i['id']
        print 'Recorded twits', recorded_twits.count()
        
        if recorded_twits.count() < 1 :
            print 'Twit ini belum disimpan ', i['text']
            
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
            response = urllib2.urlopen(link_url)
            link_url = response.url
            
            hashed_url = hashlib.sha1(link_url).hexdigest()
            recorded_links = twits.find({'hashed_url' : hashed_url})
            
            if recorded_links.count() < 1 :
                print 'Link ini belum disimpan : ', link_url
                content = url_description(link_url)
                content = content['result']
                
                link = {
                    'title' : content['title'],
                    'description' : content['content'],
                    'url' : link_url,
                    'username' : i['from_user'],
                    'count' : 0,
                    'created' : datetime.datetime.utcnow(),
                    'hashed_url' : hashed_url
                }
                
                links.insert(link)
                print 'Save ', i['id']
            else :
                print 'Link ini sudah pernah disimpan, update saja ', url
                links.update({'_id' : recorded_links['_id'], 'count' : recorded_links['count'] + 1})
        else :
            print 'Twit ini sudah pernah diproses. Skip ', i['text']
    
    return render_template('scan.html', data = 'done')
    
def url_description(link_url) :
    #url = 
    conn = pycurl.Curl()
    b = StringIO.StringIO()
    
    conn.setopt(pycurl.URL, 'http://api.digaku.com/fetch_url?u='+link_url+'&api_key=7956939c25fabef254a3eafbdff50ee0e829f6d1')
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform() 
    
    return json.loads(b.getvalue())
    

app.run(debug = True)
    
