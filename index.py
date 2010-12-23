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
    
    twitter_search = 'http://search.twitter.com/search.json?q=http+filter:links+-mtw.tl+-4sq.com+-tmi.me+-myloc.me+-tl.gd+include%3Aretweets&geocode='+city+'%2C100km'
    data = url_description(twitter_search)
    data = json.loads(data)
    
    flit = Connection().flit    
    twits = flit.twits
    links = flit.links
    
    for i in data :        
        recorded_twits = twits.find({'twit_id' : i.id})
        
        if recorded_twits.count < 1 :
            
            twit = {
                'text' : i.text,
                'username' : i.from_user,
                'created' : datetime.datetime.utcnow(),
                'twit_id' : i.id
            }
            twits.insert(twit)
            
            import re
            link_url = re.search("(?P<url>https?://[^\s]+)", i.text).group("url")
            
            import urllib2
            response = urllib2.urlopen(i.url)
            url = response.url
            
            hashed_url = hashlib.sha1(url).hexdigest()
            recorded_links = twits.find({'hashed_url' : hashed_url})
            
            if recorded_links.count < 1 :
                content = url_description('http://api.digaku.com/fetch_url?u='+url+'&api_key=7956939c25fabef254a3eafbdff50ee0e829f6d1')                
                
                link = {
                    'title' : content['title'],
                    'description' : content['content'],
                    'username' : i.from_user,
                    'count' : 0,
                    'created' : datetime.datetime.utcnow()
                }
                
                links.insert(link)
            else :
                links.update({'_id' : recorded_links['_id'], 'count' : recorded_links['count'] + 1})
    
    return render_template('scan.html', data = 'done')
    
def url_description(url) :
    conn = pycurl.Curl()
    b = StringIO.StringIO()
    
    conn.setopt(pycurl.URL, url)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform() 

    data = b.getvalue()
    return json.loads(data['result'])
    

app.run(debug = True)
    
