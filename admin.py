from StringIO import StringIO
from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from models import Author, Signatures
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



class ModerateHandler(webapp.RequestHandler):
    def _blog_fetch_callback(self, rpc):

        content = rpc.get_result().content
        d = feedparser.parse(StringIO(content))
        s = Signatures.get_single()
        signatures_and_times = dict(zip(s.hashes, s.times))
        posts = []
        for entry in d['entries']:
            author =  Author.get_or_insert(key_name=entry["source"]["id"],
                title=entry["source"]["title"],
                name=entry["author"])
            signature_key = Signatures.signature_key_for_post(entry)
            signature_time = signatures_and_times.get(signature_key)
            post = {"title": entry["title"],
                    "tags": entry.get("tags", "NOTAGS!!!!"),
                    "content": entry["content"][0]["value"],
                    "author": author,
                    "signature_time": signature_time,
                    "signature_key": signature_key}
            posts.append(post)

        template_values = {"posts":posts}

        template = jinja_environment.get_template('moderate.html')
        self.response.out.write(template.render(template_values))



    def _create_callback(self, rpc):
        return lambda: self._blog_fetch_callback(rpc)

    def get(self):
        rpc = urlfetch.create_rpc(deadline=3)
        rpc.callback = self._create_callback(rpc)
        urlfetch.make_fetch_call(rpc, FEED_URL)

        rpc.wait()
        self.response.out.write('fetch blogs')


app = webapp.WSGIApplication([('/admin/moderate', ModerateHandler),
                              ('/admin/signature_toggle/(.+)', SignatureToggleHandler)
                            ],
                             debug=DEBUG)

