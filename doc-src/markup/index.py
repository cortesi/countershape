import countershape
from countershape import markup
from countershape.doc import *

this.markup = markup.Markdown(extras=["code-friendly"])

pages = [
            Page(
                "markdown/markdown.md",
                title="Markdown",
                pageTitle = "Mark Up with MarkDown"
            ),
            Directory("markdown"),
            
            Page(
                "rest/rest.rst",
                title="reStructuredText",
                pageTitle = "reStructuredText"
            ),           
            Directory("rest"),            
        ]
        
