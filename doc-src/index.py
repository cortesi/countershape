import countershape
from countershape import Page, Directory, PythonModule, markup
from countershape.doc import *
          
this.markup = markup.Markdown(extras=["code-friendly"])

this.layout = countershape.Layout("_layout.html")
this.titlePrefix = "Countershape "

this.stdHeaders = [
    model.UrlTo("media/css/reset-fonts-grids-base.css"),
    model.UrlTo("media/css/docstyle-default.css"),
    model.UrlTo("media/css/docstyle-customised.css"),
    model.UrlTo("media/css/syntax.css"),
]
ns.docTitle = "Countershape Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "dev@nullcube.com"
ns.copyright = "Copyright Nullcube 2007"
ns.head = countershape.template.File(None, "_banner.html")
ns.sidebar = countershape.widgets.SiblingPageIndex(
            '/index.html', 
            exclude=['countershape']
          )
pages = [
    Page("index.html", 
        title="Introduction",
        pageTitle="Introduction to Countershape"
        ),
    Directory("install"),
        
    Page("markup/markup.md", 
        title="Page Markup",
        pageTitle="Page Markup Options"
        ),
    Directory("markup"),
    
    PythonModule("../countershape", 
        title="Source"),
        
    Page("admin.html", 
        title="Administrivia",
        pageTitle="Novella Administrivia")
    
]

ns.imgBanner = countershape.html.IMG(
    src=countershape.model.UrlTo("countershape.png"),
    width="280",
    height="77",
    align="right"
    )
