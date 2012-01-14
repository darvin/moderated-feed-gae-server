from StringIO import StringIO
import os
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
import jinja2
from models import Author, Signatures, BlogPost
from settings import FEED_URL, DEBUG
from utils import feedparser
feedparser.SANITIZE_HTML = 0
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), "templates")))


class MainHandler(webapp.RequestHandler):
    def _blog_fetch_callback(self, rpc):

        content = rpc.get_result().content
        d = feedparser.parse(StringIO(content))
        signatures = Signatures.signatures()
        posts = []
        for entry in d['entries']:
            blog_post = BlogPost.blog_post_from_feed_entry(entry)
            if blog_post.signature in signatures:
                posts.append(blog_post)

        template_values = {"posts":posts, "DEBUG":DEBUG}

        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render(template_values))



    def _create_callback(self, rpc):
        return lambda: self._blog_fetch_callback(rpc)

    def get(self):
        rpc = urlfetch.create_rpc(deadline=3)
        rpc.callback = self._create_callback(rpc)
        urlfetch.make_fetch_call(rpc, FEED_URL)

        rpc.wait()
        self.response.out.write('fetch blogs')


app = webapp.WSGIApplication([('/', MainHandler)],
                             debug=DEBUG)

