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
            Template(False, readFrom("_layout.html"))
        )
this.layout = ExampleLayout()
blog = blog.Blog("My Blog", "my blog description", "http://foo", "posts", "../blog-posts")
pages = [
    blog(),
    blog.index("index.html", "Blog"),
    Page("about.html", "About"),
    blog.archive("archive.html", "Archive"),
    blog.rss("rss.xml", "RSS"),
]
