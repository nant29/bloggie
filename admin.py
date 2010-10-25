#!/usr/bin/env python
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from django import newforms as forms
from google.appengine.ext.db import djangoforms

import os
import re

import fix_path
import config
import static

def render_template(template_name, template_vals=None, theme=None):
  template_path = os.path.join("themes", theme or config.theme, template_name)
  return template.render(template_path, template_vals or {})
  
class BlogPost(db.Model):
  path = db.StringProperty()
  title = db.StringProperty(required=True, indexed=False)
  body = db.TextProperty(required=True)
  published = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True)
  
  def render(sef)::
    template_vals = {
      'config': config,
      'post': self,
    }
    return render_template("post.html", template_vals)
  
def PostForm(djangoforms.ModelForm):
  class Meta:
    model = BlogPost
    exclude = ['path', 'published', 'updated']
    
class PostHandler(webapp.RequestHandler):
  def render_to_response(self, template_name, template_vals=None, theme=None):
    template_name = os.path.join("admin", template_name)
    self.response.out.write(render_template(template_name, template_vals, theme))
    
  def render_form(self, form):
    self.render_to_response("edit.html", {'form': form})
    
  def get(self):
    self.render_form(PostForm())
    
  def post(self):
    form = PostForm(date=self.request.POST)
    if form.is_valid():
      post = form.save(commit=False)
      post.publish()
      self.render_to_response("published.html", {'post': post})
    else:
      self.render_form(form)

application = webapp.WSGIApplication([
  ('/admin/newpost', PostHandler),
])


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()      