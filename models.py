import aetycoon
import re
from google.appengine.ext import db
from google.appengine.ext import deferred

import config
import generators
import static
import utils

class BlogPost(db.Model):
  MIME_TYPE = "text/html; charset=utf-8"
  
  path = db.StringProperty()
  title = db.StringProperty(required=True, indexed=False)
  body = db.TextProperty(required=True)
  published = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True)
  deps = aetycoon.PickleProperty()
  
  @property
  def summary(self):
    match = re.search("<!--.*cut.*-->", self.body)
    if match:
      return self.body[:match.start(0)]
    else:
      return self.body
      
  def publish(self):
    rendered = self.render()
    if not self.path:
      num = 0
      content = None
      while not content:
        path = format_post_path(self, num)
        content = static.add(path, rendered, "text/html")
        num += 1
        self.path = path
        self.put()
      else:
        static.set(self.path, rendered, "text/html")
