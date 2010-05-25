Countershape supports documentation markup in a number of formats, including:

- HTML
- [Markdown](markup/markdown.html)
- reStructuredText ReST
- [Textish](markup/textish.html)

### reStructuredText Using docutils.sourceforge.net

Use a page filename with the file extension ".rst" or from the referencing index.py
use:

`this.markup = "rst"`

[reStructuredText](http://docutils.sourceforge.net/rst.html) is an easy-to-read, 
what-you-see-is-what-you-get plaintext markup syntax and parser system. It is 
useful for in-line program documentation (such as Python docstrings), for quickly 
creating simple web pages, and for standalone documents. reStructuredText is 
designed for extensibility for specific application domains. The reStructuredText 
parser is a component of Docutils. 

reStructuredText is a revision and reinterpretation of the StructuredText and
Setext lightweight markup systems


### Markdown using markdown2

[Markdown](http://daringfireball.net/projects/markdown/) is a text-to-HTML 
conversion tool for web writers. Markdown allows you to write using an 
easy-to-read, easy-to-write plain text format, then convert it to structurally 
valid XHTML (or HTML). 

### Textish (default)

`this.markup = "textish"`

Textish is a text mark-up syntax processed by countershape

With the support of external tools (ala pygments) Countershape also supports
code coloring syntax for :

- Python
- Python Tracebacks
- CSS
- HTML
- Javascript
- Cc