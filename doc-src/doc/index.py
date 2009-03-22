from countershape.doc import *
import cubictemp

def escape(s):
    return '<div class="highlight"><pre>%s</pre></div>'%cubictemp.escape(s)

ns.textish = escape

pages = [
    Page("structure.html", "Document Structure"),
    Page("textish.html", "Textish"),
    Page("code.html", "Documenting Code"),
]
