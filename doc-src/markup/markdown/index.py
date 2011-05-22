from countershape.doc import *
from countershape import markup
this.markup = markup.Markdown(extras=["code-friendly"])

pages = [
    Page("basics.text", "Basics"),
    Page("syntax.text", "Syntax"),
]
