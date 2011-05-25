import countershape
from countershape import markup
from countershape.doc import *

this.markup = markup.Markdown(extras=["code-friendly"])

pages = [
            Page(
                "install.mdtext",
                title="Install",
                pageTitle = "Installation"
            ),           

            Page(
                "config.mdtext",
                title="Config",
                pageTitle = "Path Config"
            ),
            
            Page(
                "generate.mdtext",
                title="Generate Site",
                pageTitle = "Generate Site"
            ),           
            
            Page(
                "blog.mdtext",
                title="Blog",
                pageTitle = "Web Log"
            ),           
        ]
        
