import countershape
from countershape import widgets, layout, grok, blog
from countershape.doc import *

ns.foot = "This is a footer"
ns.head = "<h1>Example Blog</h2>"
ns.sidebar = widgets.SiblingPageIndex('/index.html', depth=1)
ns.readFrom = readFrom

class ExampleLayout(layout.Layout):
    components = ["pageTitle", "body", "header"]
    def __init__(self):
        layout.Layout.__init__(
            self,
            "_layout.html"
        )
this.layout = ExampleLayout()


this.stdHeaders = [
    model.UrlTo("media/css/reset.css"),
    model.UrlTo("media/css/docstyle.css"),
    model.UrlTo("media/css/content.css"),
]
    

blog = blog.Blog(
        blogname="My Blog", 
        blogdesc="my blog description", 
        url="http://foo", 
        base="src", 
        src="../blog-posts")

pages = [
    blog(),
    blog.index("index.html", "Blog"),
    Page("about.html", "About"),
    blog.archive("archive.html", "Archive"),
    blog.rss("rss.xml", "RSS"),
]
