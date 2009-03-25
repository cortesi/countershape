import countershape.layout
import countershape.template
import countershape.widgets
import countershape.grok
from countershape.doc import *

this.layout = countershape.layout.Layout("_layout.html")
this.markdown = "rst"
ns.docTitle = "Countershape Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "aldo@nullcube.com"
ns.foot = "Copyright Nullcube 2007"
ns.head = countershape.template.File(None, "_header.html")
ns.sidebar = countershape.widgets.SiblingPageIndex(
            '/index.html', exclude=['countershape']
          )
ns.cs = countershape.grok.grok("../countershape")

pages = [
    Page("index.html", "Introduction"),
    Page("structure.html", "Document Structure"),
    Page("code.html", "Documenting Code"),
    Page("api.html", "API Reference"),
    Directory("api"),
    PythonModule("../countershape", "Source"),
    Page("admin.html", "Administrivia")
]
