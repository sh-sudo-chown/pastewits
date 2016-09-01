#!/usr/bin/env python
import twitter
import requests
import pymongo
import re
import sys
from urllib2 import *

#script to collect pastes linked to by pastebin twitter bots to mongodb collection
#
#Usage
#python ./pastewits.py screen_name

def pastegrab(url):
    try:
	    test = requests.get(url, headers = {'Accept' : 'application/xml'}, timeout=5)
    except Exception, e:
	    print "failure on socket connect to " + url
	    return -1
    if test.status_code == 200:
	try:
	        pastefile = urlopen(url)
	except Exception, e:
		print "request returned status code 200, but additional request returned  code" + pastefile.geturl()
	print pastefile.geturl()
    else:
	print "opening " + url + " returned invalid status code"
	return -1
    return pastefile

def pastemongo(doc,ref,database,status):
	ref = str(ref.split("/")[(len(ref.split("/"))-1):])[3:-2]
	collection = pymongo.collection.Collection(database,ref)
	post_id = collection.insert_one(doc).inserted_id
	print "posted to collection " + ref

def pasteformat(pastefile,status,db,database,regexes,tags,ref):
	statustags = []
	pastetags = []
	for word in str(status.text).split():
		if word in tags:
			if not word in statustags:
				statustags.append(str(word))
	metadoc = {
	'tweet_id': status.id,
	'tweet_url': str(ref.split("/")[(len(ref.split("/"))-1):])[3:-2],
	'paste_url': pastefile.geturl(),
	'tweet': status.text,
	#'hashtags': status.hashtags,
	'status_tags': statustags
	}
	i=0
	for line in pastefile.readlines():
		print line
		if line != None:
			i+=1
			paste = { 'line' : i }
			for word in str(line).split():
				if word in tags:
					if not word in pastetags:
						pastetags.append(word)
			metadoc['paste_tags'] = tuple(pastetags)
			for k,v in regexes.items():
				instances = v.findall(line)
				if instances != None:
					metadoc[k] = (len(instances))
				else:
					continue
				if len(instances) >1:
					it=0
					for instance in instances:
						try:
							paste[k[it]]=str(instance)
						except Exception, e:
							print "out of range, skipping line"
							continue
						it+=1
				elif len(instances) == 1:
					try:
						paste[k]=(str(instances))
					except Exception, e:
						print "out of range, skipping line"
						continue
			paste['text'] = str(line)
   	 		pastemongo(paste,ref,database,status)
		pastemongo(metadoc,ref,database,status)
	return 0

def expressions():
	regexes = {
	'email': re.compile('[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}'),
	'ssn': re.compile('\d{3}-?\d{2}-?\d{4}'),
	'url':re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|(?<=[a-zA-z]|[0-9]|[$-_@.&+]|[!*\(\),]){2,60}\.[a-zA-Z]{2,3}\/(?=[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]){2,60}'),
	'ip': re.compile('\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
	'mac': re.compile('\b(?:[0-9A-Fa-f]{2}[:\-\.]){5}([0-9A-Fa-f]{2})\b'),
	'telephone': re.compile('\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
	'credit': re.compile('\b(\d{4}-){3}\d{4}\b')
	}
	tags = ['google', 'Google', 'GOOGLE', 'API', 'Api', 'api', 'database', 'lulz', 'SSH', 'ssh', 'Ssh', 'PGP', 'pgp', 'Pgp', 'username', 'Username', 'uname', 'Uname', 'password', 'Password', 'pword', 'Pword', 'email', 'Email', 'SQL', 'sql', 'Sql', 'NoSQL', 'nosql', 'Mongo', 'mongo', 'credit', 'Credit', 'Visa', 'VISA', 'Mastercard', 'mastercard', 'Discover', 'discover', 'American Express', 'American express', 'american express', 'AMERICAN EXPRESS' 'Amex', 'AmEx', 'AMEX',  'Paypal', 'paypal', 'PAYPAL', 'Unionpay', 'unionpay', 'UNIONPAY', 'Maestro', 'maestro', 'MAESTRO', 'Jcb', 'JCB', 'jcb', 'Twitter', 'twitter', 'TWITTER', 'Metasploit', 'metasploit', 'SET', 'Social Engineering Toolkit', 'social engineer', 'Social engineer', 'Social Engineer', 'hash', 'Hash', 'Github', 'github', 'GITHUB', 'wifi', 'WIFI', 'Android', 'android', 'Apple', 'apple', 'APPLE', 'Cisco', 'cisco', 'CISCO', 'config', 'CONFIG', 'Config', 'router', 'Router', 'address', 'Address', 'MAC', 'mac address', 'Mac Address', 'IP', 'ip address', 'Ip address', 'IP Address']
	return regexes, tags

def get_tweets(api,db,database):
    urlpattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|(?<=[a-zA-z]|[0-9]|[$-_@.&+]|[!*\(\),]){2,60}\.[a-zA-Z]{2,3}\/(?=[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]){2,60}')
    regexes, tags = expressions()
    maxid = None
    while maxid != -1:
	#continue iterable, GetUserTimeline will throw error on complete
	try:
	        statuses = api.GetUserTimeline(screen_name=db, count=20, max_id=maxid)
	except Exception, e:
		print "Twitter cannot find more tweets after " + str(maxid)
		sys.exit(0)
	for status in statuses:
	    url = urlpattern.findall(status.text)
	    print url
            for ref in url:
		    if ref:
			    pastefile = pastegrab(ref)
			    if pastefile != -1:
				   pasteformat(pastefile,status,db,database,regexes,tags,ref)
	    maxid=status.id

if __name__ == "__main__":
    api=twitter.Api(
	#add personal app info here
	consumer_key = 'myD7iaPP8hXqho5V0495dR2yo',
	consumer_secret = 't5THfDrPVhW2Ac3H0vfo07tIKSWhhcQUEhvUyJwKJApcTrXku9',
	access_token_key = '2520209895-TZzj7wGWhkXW5GUX0QSKdUcRzHvRjqECTNVwwpV',
	access_token_secret = 'WuJc6d0GoT8okfQHdkcydRyWS2ZapjmLYsqsGScQ58CUe',
        sleep_on_rate_limit=True
    )
    db = str(sys.argv[1])
#    maxid = sys.argv[2]
    client = pymongo.MongoClient('localhost',27017)
    database = pymongo.database.Database(client,db)
    get_tweets(api,db,database)
