import countershape
from countershape import Page, Directory, PythonModule
import countershape.grok


this.layout = countershape.Layout("_layout.html")
this.markdown = "rst"
ns.docTitle = "Countershape Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "dev@nullcube.com"
ns.copyright = "Copyright Nullcube 2007"
ns.head = countershape.template.File(None, "_banner.html")
ns.sidebar = countershape.widgets.SiblingPageIndex(
            '/index.html', 
            exclude=['countershape']
          )
ns.parse = countershape.grok.parse("../countershape")

pages = [
    Page("index.html", "Introduction"),
    Page("structure.html", "Document Structure"),
    Page("doc.html", "Documenting Code"),
    Page("api/apiref.html", "API Reference"),
    Directory("api"),
    PythonModule("../countershape", "Source"),
    Page("admin.html", "Administrivia")
]

ns.imgBanner = countershape.html.IMG(
    src=countershape.model.UrlTo("countershape.png"),
    width="280",
    height="77",
    align="right"
    )