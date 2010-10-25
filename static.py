#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import datetime
import hashlib

import fix_path
import aetycoon

import aetycoon

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

class StaticContent(db.Model):
	body = db.BlobProperty()
	content_type = db.StringProperty(required=True)
	last_modified = db.DateTimeProperty(required=True, auto_now=True)
	etag = aetycoon.DerivedProperty(lambda x: hashlib.sha1(x.body).hexdigest())

def get(path):
	return StaticContent.get_by_key_name(path)
	
def set(path, body, content_type, **kwargs):
	content = StaticContent(
		key_name=path,
		body=body,
		content_type=content_type,
		**kwargs)
		
	content.put()
	return content
		
def add(path, body, content_type, **kwargs):
  def _tx():
    if StaticContent.get_by_key_name(path):
      return None
    return set(path, body, content_type, **kwargs)
  return db.run_in_transaction(_tx)
  
class StaticContentHandler(webapp.RequestHandler):
	def output_content(self, content, serve=True):
		self.response.headers['Content-Type'] = content.content_type
		last_modified = content.last_modified.strftime(HTTP_DATE_FMT)
		self.response.headers['Last-Modified'] = last_modified
		self.response.headers['ETag'] = '"%s"' % content.etag
		
		if serve:
			self.response.out.write(content.body)
		else:
			self.response.set_status(304)
			
	def get(self, path):
		content = get(path)
		if not content:
			self.error(404)
			return
		
		serve = True
		if 'If-Modified-Since' in self.request.headers:
			last_seen = datetime.datetime.strptime(
				self.request.headers['If-Modified-Since'],
				HTTP_DATE_FMT)
			if last_seen >= content.last_modified.replace(microsecond=0):
				serve = False
		if 'If-None-Match' in self.request.headers:
			etags =[x.strip()
							for x in self.request.headers['If-None-Match'].split(',')]
			if content.etag in etags:
				server = False
		self.output_content(content, serve)
		
application = webapp.WSGIApplication([('(/.*)', StaticContentHandler)])

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
