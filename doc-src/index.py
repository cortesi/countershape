import countershape
from countershape import Page, Directory, PythonModule, markup
from countershape.doc import *
          
this.markup = markup.Markdown(extras=["code-friendly"])

this.layout = countershape.Layout("_layout.html")
this.titlePrefix = "Countershape "

this.stdHeaders = [
    widgets.UrlTo("media/css/reset-fonts-grids-base.css"),
    widgets.UrlTo("media/css/docstyle-default.css"),
    widgets.UrlTo("media/css/docstyle-customised.css"),
    widgets.UrlTo("media/css/syntax.css"),
]
this.metadata = {
    "robots":"all",
    "keywords":"countershape,website generator,website compiler",
    "description":"Countershape website generator",
    "copyright":"(c) Copyright Nullcube 2007"
}
ns.docTitle = "Countershape Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "dev@nullcube.com"
ns.copyright = "Copyright Nullcube 2007"
ns.head = countershape.template.File(None, "_banner.html")
ns.sidebar = countershape.widgets.SiblingPageIndex(
            '/index.html'
          )
ns.license = file("../LICENSE").read()

ns.imgBanner = countershape.html.IMG(
    src=countershape.widgets.UrlTo("countershape.png"),
    width="280",
    height="77",
    align="right"
    )

class ShowSrc:
    def __init__(self, d):
        self.d = os.path.abspath(d)
    
    def __call__(self, path):
        return countershape.doc.readFrom(os.path.join(self.d, path))

ns.readFrom = ShowSrc(".")        

pages = [
    Page("index.md", 
        title="Introduction",
        pageTitle="Introduction to Countershape"
        ),
    Directory("intro"),
        
    Page("markup/markup.md", 
        title="Text Formatting",
        pageTitle="Text Formatting Options"
        ),
    Directory("markup"),
    
    PythonModule(name="../countershape", 
        title="Source"),
        
    Page("admin.md", 
        title="Administrivia",
        pageTitle="Novella Administrivia")
    
]
