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
    if not self.path:
      num = 0
      content = None
      while not content:
        path = utils.format_post_path(self, num)
        content = static.add(path, '', config.html_mime_type)
        num += 1
      self.path = path
    if not self.deps:
      self.deps = {}
    self.put()
    for generator_class in generators.generator_list:
      new_deps = set(generator_class.get_resource_list(self))
      new_etag = generator_class.get_etag(self)
      old_deps, old_etag = self.deps.get(generator_class.name(), (set(), None))
      if new_etag != old_etag:
        to_regenerate = new_deps | old_deps
      else:
        to_regenerate = new_deps ^ old_deps
      for dep in to_regenerate:
        generator_class.generate_resource(self, dep)
      self.deps[generator_class.name()] = (new_deps, new_etag)
    self.put()