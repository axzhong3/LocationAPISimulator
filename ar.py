import webapp2
import jinja2

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Main(Handler):
    def render_front(self):
        self.render("index.html")
    
    def get(self):
        self.render_front()

application = webapp2.WSGIApplication([
    ('/', Main)
], debug = True)
