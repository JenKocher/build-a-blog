#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import db
import jinja2
import os
import webapp2

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPostKind(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogHandler(Handler):
    def render_blog(self, blogpost=""):
        blogposts = db.GqlQuery("SELECT * from BlogPostKind ORDER BY created DESC LIMIT 5")
        self.render("blog.html", blogposts=blogposts)

    def get(self):
        self.render_blog()

class NewPostHandler(Handler):
    def render_main(self, title="", blogpost="", error=""):
        self.render("newpost.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_main()

    def post(self):
        title   = self.request.get('title')
        blogpost = self.request.get('blogpost')

        if title and blogpost:
#            blogpost.replace('\n', '<br>')   Don't need this with <pre></pre>
            BlogPostEntity = BlogPostKind(title = title, blogpost = blogpost)
            BlogPostEntity.put()
            post_id = BlogPostEntity.key().id()
            post_id = str(post_id)
            URL_string = '/blog/' + post_id
            self.redirect(URL_string)
        else:
            error = "We need both a title and a blogpost."
            self.render_main(title, blogpost, error)

class ViewPostHandler(Handler):
    def get(self, post_id):
        BlogPostEntity = BlogPostKind.get_by_id(int(post_id))
        self.render("singlepost.html", blogpost=BlogPostEntity, post_id = post_id)

app = webapp2.WSGIApplication([
    ('/blog/newpost', NewPostHandler),
    ('/blog', BlogHandler),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler),
], debug=True)
