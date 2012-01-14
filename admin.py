from StringIO import StringIO
from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from models import Author, Signatures, Tags, BlogPost
from utils import feedparser
feedparser.SANITIZE_HTML = 0
from settings import FEED_URL, DEBUG
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), "templates")))

class SignatureToggleHandler(webapp.RequestHandler):
    def get(self, signature_hash):
        signatures = Signatures.signatures()
        if signature_hash not in signatures:
            Signatures.add_signature(signature_hash)
        else:
            Signatures.remove_signature(signature_hash)
        self.redirect("/admin/moderate")


class TagToggleHandler(webapp.RequestHandler):
    def get(self, tag):
        tags_entity = Tags.get_single()
        if tag in tags_entity.available:
            if tag not in tags_entity.enabled:
                tags_entity.enabled.append(tag)
                tags_entity.save()
            else:
                tags_entity.enabled.remove(tag)
                tags_entity.save()
        self.redirect("/admin/tags")



class TagsHandler(webapp.RequestHandler):

    def get(self):

        tags = Tags.get_single()

        template_values = {"tags_enabled":tags.enabled,
                           "tags_available":tags.available}

        template = jinja_environment.get_template('tags.html')
        self.response.out.write(template.render(template_values))


class ModerateHandler(webapp.RequestHandler):
    def _blog_fetch_callback(self, rpc):

        content = rpc.get_result().content
        d = feedparser.parse(StringIO(content))
        s = Signatures.get_single()
        signatures_and_times = dict(zip(s.hashes, s.times))
        posts = []

        tags_entity = Tags.get_single()
        tags = set(tags_entity.available)

        for entry in d['entries']:
            blog_post = BlogPost.blog_post_from_feed_entry(entry)
            signature_time = signatures_and_times.get(blog_post.signature)
            posts.append((blog_post, signature_time))

            for tag in blog_post.tags:
                tags.add(tag.lower())

        template_values = {"posts":posts}

        tags_entity.available = list(tags)
        tags_entity.save()

        template = jinja_environment.get_template('moderate.html')
        self.response.out.write(template.render(template_values))



    def _create_callback(self, rpc):
        return lambda: self._blog_fetch_callback(rpc)

    def get(self):
        rpc = urlfetch.create_rpc(deadline=3)
        rpc.callback = self._create_callback(rpc)
        urlfetch.make_fetch_call(rpc, FEED_URL)

        rpc.wait()


app = webapp.WSGIApplication([('/admin/moderate', ModerateHandler),
                              ('/admin/signature_toggle/(.+)', SignatureToggleHandler),
                              ('/admin/tags', TagsHandler),
                              ('/admin/tag_toggle/(.+)', TagToggleHandler),
                            ],
                             debug=DEBUG)

