import countershape
from countershape import markup
from countershape.doc import *

this.markup = markup.Markdown(extras=["code-friendly"])

pages = [
            Page(
                "install.md",
                title="Install",
                pageTitle = "Installation"
            ),           

            Page(
                "config.md",
                title="Config",
                pageTitle = "Path Config"
            ),
            
            Page(
                "generate.md",
                title="Generate Site",
                pageTitle = "Generate Site"
            ),           
            
            Page(
                "blog.md",
                title="Blog",
                pageTitle = "Web Log"
            ),           
        ]
        
