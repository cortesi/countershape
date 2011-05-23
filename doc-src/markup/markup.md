Countershape supports documentation markup in a number of formats, including:

- HTML
- [Markdown](markup/markdown.html)
- reStructuredText ReST

The markup can be specific to a site or particular path, using the classes
specified in markup.py and referenced as in the below:

### reStructuredText Using docutils.sourceforge.net

Use a page filename with the file extension ".rst" or from the configuration index.py
use:

`this.markup = markup.RST()`

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

Use a page filename with the file extension ".mdtext" or from the configuration index.py
use:

`this.markup = markup.Markdown()`

Options for the markdown2 command-line utility can be included such as:

`this.markup = markup.Markdown(extras=["code-friendly"])`
