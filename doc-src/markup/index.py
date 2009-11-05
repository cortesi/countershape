from countershape.doc import *
this.markdown = "rst"

ns.docTitle = "Document Structure"
pages = [
    Page("textish/textish.html", "Textish"),
    Directory("textish"),
    Page("markdown/markdown.html", "Markdown"),
    Directory("markdown"),
    
]
