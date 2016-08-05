# -*- coding: utf-8 -*-
import boto
import boto.s3.connection
from boto.s3.key import Key
from flask import Flask, render_template, request
import time
import csv
import urllib
import os

access_key = 'access_key'
secret_key = 'secret_key'

rdsHost = "instanceURL"
userName = "dbusername"
password = "dbpassword"
dbName = "dbname"
bucketURL = "bucketURL"
bucketName = 'bucketName'

conn = boto.connect_s3(access_key, secret_key)
application = Flask(__name__)

def getBucketContentsTerminal():
	bucket = conn.get_bucket(bucketName, validate=False)
	nameList = []
	sizeList = []
	for key in bucket.list():
		fileName = getFileName(key.name)
			nameList.append(fileName)
			sizeList.append(key.size)
	return (nameList, sizeList)

@application.route('/')
def getBucketContents():
	nameList, sizeList = getBucketContentsTerminal()
	return render_template("bucketContents.html", nameList=nameList, sizeList=sizeList)

@application.route('/listBuckets')
def listBuckets():
	bucketList = conn.get_all_buckets()
	return render_template("bucketListing.html", bucketList=bucketList)

@application.route('/uploadFile', methods=['POST'])
def uploadFile():
	file = request.files['file']
	key = request.files['file'].filename
	content_type = None
	callback = None
	md5 = None
	reduced_redundancy = False
	size = file.tell()
	bucket = conn.get_bucket(bucketName, validate=False)
	k = Key(bucket)
	k.key = key
	if content_type:
		k.set_metadata('Content-Type', content_type)
	startTime = time.time()
	sent = k.set_contents_from_file(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy, rewind=True)
	timeTaken = time.time() - startTime
	# Rewind for later use
	file.seek(0)

	nameList, sizeList = getBucketContentsTerminal()
	return render_template("timedBucketContents.html", nameList=nameList, sizeList=sizeList,timeTaken=timeTaken)

def getFileName(filePath):
	try:
		slashIndex = filePath.rindex("/")
		periodIndex = filePath.rindex(".")
		return filePath[slashIndex+1:periodIndex]
	except ValueError:
		slashIndex = 0
		periodIndex = len(filePath)
		return filePath[slashIndex:periodIndex]

def main():
	application.debug = True
	application.run()
	
if __name__=='__main__': main()