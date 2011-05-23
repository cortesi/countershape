Use a page filename with the file extension ".mdtext", ".md" or from the configuration
index.py use:

<pre>
import countershape
from countershape import markup
this.markup = markup.Markdown()
</pre>

to render all pages using this markdown2.

Options for the markdown2 command-line utility can be included such as:

`this.markup = markup.Markdown(extras=["code-friendly"])`

Refer to the [python-markdown2](https://github.com/trentm/python-markdown2) project
site for installation, and more complete documentation.

[Markdown](http://daringfireball.net/projects/markdown/) is a text-to-HTML 
conversion tool for web writers. Markdown allows you to write using an 
easy-to-read, easy-to-write plain text format, then convert it to structurally 
valid XHTML (or HTML). 

Thus, "Markdown" is two things: (1) a plain text formatting syntax;
and (2) a software tool, written in Perl, that converts the plain text
formatting to HTML. See the Syntax page for details pertaining to
Markdown s formatting syntax. You can try it out, right now, using the online
[Dingus](http://daringfireball.net/projects/markdown/dingus).