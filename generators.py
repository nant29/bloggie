import hashlib
from google.appengine.ext import db

import fix_path
import config
import static
import utils

generator_list = []

class ContentGenerator(object):
  @classmethod
  def name(cls):
    return cls.__name__
    
  @classmethod
  def get_resource_list(cls, post):
    raise NotImplementedError()
    
  @classmethod
  def get_etag(cls, post):
    raise NotImplementedError()
    
  @classmethod
  def generate_resource(cls, post, resource):
    raise NotImplementedError()
    
class PostContentGenerator(ContentGenerator):
  """Content generator for the actual blog post itself."""
  
  @classmethod
  def get_resource_list(cls, post):
    return [post.path]
    
  @classmethod
  def get_etag(cls, post):
    return hashlib.sha1(db.model_to_protobuf(post).Encode()).hexdigest()
    
  @classmethod
  def generate_resource(cls, post, resource):
    assert resource == post.path
    template_vals = {
      'post': post
    }
    rendered = utils.render_template("post.html", template_vals)
    static.set(post.path, rendered, config.html_mime_type)
generator_list.append(PostContentGenerator)

class IndexContentGenerator(ContentGenerator):
  """ContentGenerator for the homepage of the blog and archive pages."""
  
  @classmethod
  def get_resource_list(cls, post):
    return ["index"]
    
  @classmethod
  def get_etag(cls, post):
    return hashlib.sha1(post.title + post.summary).hexdigest()
    
  @classmethod
  def generate_resource(cls, post, resource):
    assert resource == "index"
    import models
    q = models.BlogPost.all().order('-published')
    posts = q.fetch(config.posts_per_page)
    template_vals = {
      'posts': posts,
    }
    rendered = utils.render_template("listing.html", template_vals)
    static.set('/', rendered, config.html_mime_type)
generator_list.append(IndexContentGenerator)
