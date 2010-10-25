
from google.appengine.ext import db

class StaticContent(db.Model):
	body = db.BlobProperty()
	content_type = db.StringProperty(required=True)