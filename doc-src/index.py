import countershape
from countershape import Page, Directory, PythonModule
import countershape.grok
from countershape.doc import *

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
#~ ns.parse = countershape.grok.parse("../countershape")

pages = [
    Page("index.html", 
        title="Introduction",
        pageTitle="Introduction to Countershape"
        ),
        
    Page("markup/markup.md", 
        title="Document Markup",
        pageTitle="Document Markup Options"
        ),
    Directory("markup"),
    
    Page("code/code.html", 
        title="Documenting Code",
        pageTitle="Documenting Code"
        ),
    Directory("code"),
    
    Page("api/apiref.html", 
        title="API Reference",
        pageTitle="API Reference"
        ),
    Directory("api"),
    
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
