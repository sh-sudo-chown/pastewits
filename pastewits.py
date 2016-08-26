#!/usr/bin/env python
import twitter
import requests
import pymongo
import re
import sys
from urllib2 import urlopen

#script to collect pastes linked to by pastebin twitter bots to mongodb collection
#
#Usage
#python ./pastewits.py screen_name

def pastegrab(url):
    try:
	    test = requests.get(url, headers = {'Accept' : 'application/xml'}, timeout=5)
    except Exception, e:
	    print "failure on socket connect to " + url
	    return 0
    if test.status_code == 200:
        paste = pasteformat(url)
    else:
	print "opening " + url + " returned invalid status code"
	return 0
    return paste

def pastemongo(paste,ref,database):
    ref = str(ref.split("/")[(len(ref.split("/"))-1):])[3:-2]
    collection = pymongo.collection.Collection(database,ref)
    post_id = collection.insert_one(paste).inserted_id
    print "posted to collection " + ref

def pasteformat(url):
	pastefile = urlopen(url)
	print pastefile.geturl()
	for line in pastefile.readlines():
		print line
		if len(line.split(':')) > 1:
			paste = {line.split(':')[0].strip() : line.split(':')[1:]}
		elif len(line.split('@')) == 2:
			paste = {line.strip() : '<blank>'}
	return paste

def get_tweets(api,db,datanbase):
    maxid = None
    urlpattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|(?<=[a-zA-z]|[0-9]|[$-_@.&+]|[!*\(\),]){2,60}\.[a-zA-Z]{2,3}\/(?=[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]){2,60}')
    while maxid != -1:
	#continue iterable, GetUserTimeline will throw error on complete
	try:
	        statuses = api.GetUserTimeline(screen_name=db, count=20, max_id=maxid)
	except Exception, e:
		print "Twitter cannot find more tweets after " + str(max_id)
		sys.exit(0)
	for status in statuses:
	    url = urlpattern.findall(status.text)
	    print url
            for ref in url:
		    if ref:
			    paste = pastegrab(ref)
			    if paste != 0:
	    	   		    pastemongo(paste,ref,database)
	    maxid=status.id

if __name__ == "__main__":
    api=twitter.Api(
	consumer_key = 'myD7iaPP8hXqho5V0495dR2yo',
	consumer_secret = 't5THfDrPVhW2Ac3H0vfo07tIKSWhhcQUEhvUyJwKJApcTrXku9',
	access_token_key = '2520209895-TZzj7wGWhkXW5GUX0QSKdUcRzHvRjqECTNVwwpV',
	access_token_secret = 'WuJc6d0GoT8okfQHdkcydRyWS2ZapjmLYsqsGScQ58CUe',
        sleep_on_rate_limit=True
    )
    db = str(sys.argv[1])
    client = pymongo.MongoClient('localhost',27017)
    database = pymongo.database.Database(client,db)
    get_tweets(api,db,database)
