import countershape
from countershape import widgets, layout, markup, blog
from countershape.doc import *
this.site_url="http://foo"
this.markup = markup.Markdown(extras=["code-friendly"])

ns.foot = "This is a footer"
ns.head = "My Example Blog"
ns.sidebar = widgets.SiblingPageIndex('/index.html', depth=1)

this.layout = layout.Layout("_layout.html")

this.stdHeaders = [
    model.UrlTo("media/css/reset.css"),
    model.UrlTo("media/css/docstyle.css"),
    model.UrlTo("media/css/content.css"),
]
    

blog = blog.Blog(
        blogname="My Blog", 
        blogdesc="my blog description", 
        base="src", 
        src="../blog-posts")

pages = [
    blog(),
    blog.index("index.html", "My Example Blog"),
    Page("about.mdtext", "About"),
    blog.archive("archive.html", "Archive"),
    blog.rss("rss.xml", title="My Blog RSS", fullrss=True),
]
