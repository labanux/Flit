import pycurl
import StringIO
import json
from pymongo import Connection

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

STREAM_URL = 'http://search.twitter.com/search.json?q=http+filter:links+-mtw.tl+-4sq.com+-tmi.me+-myloc.me+-tl.gd+include%3Aretweets&geocode='+city+'%2C100km'
conn = pycurl.Curl()
b = StringIO.StringIO()

conn.setopt(pycurl.URL, STREAM_URL)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform() 

data = b.getvalue()
data = json.loads(data)

for i in data['results'] :
    print i['text']
