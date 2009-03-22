import countershape.layout
import countershape.widgets
import countershape.grok
from countershape.doc import *

class CSLayout(countershape.layout.Layout):
    components = ["pageTitle", "body", "header"]
    def __init__(self):
        countershape.layout.Layout.__init__(
            self,
            Template(False, readFrom("_layout.html"))
        )
this.layout = CSLayout()

ns.docTitle = "Countershape Manual"
ns.docMaintainer = "Aldo Cortesi"
ns.docMaintainerEmail = "aldo@nullcube.com"
ns.foot = "Copyright Nullcube 2007"
ns.head = readFrom("_header.html")
ns.sidebar = countershape.widgets.SiblingPageIndex(
            '/index.html', exclude=['countershape']
          )
ns.cs = countershape.grok.grok("../countershape")

pages = [
    Page("index.html", "Introduction"),
    Page("start.html", "Getting Started"),
    Page("doc.html", "Static Sites"),
    Directory("doc"),
    Page("api.html", "API Reference"),
    Directory("api"),
    PythonModule("../countershape", "Source"),
    Page("admin.html", "Administrivia")
]
