Use a page filename with the file extension ".rst" or ".rest" to render
that specific document using this markup context. Likewise, within the 
configuration file index.py that calls countershape.docs.Page("yourfile.text"), 
use::

    import countershape
    from countershape import markup
    this.markup = markup.RST()

to render all pages in the index.py using this markup context.

`reStructuredText <http://docutils.sourceforge.net/rst.html>`_ is an easy-to-read, 
what-you-see-is-what-you-get plaintext markup syntax and parser system. It is 
useful for in-line program documentation (such as Python docstrings), for quickly 
creating simple web pages, and for standalone documents. reStructuredText is 
designed for extensibility for specific application domains. The reStructuredText 
parser is a component of Docutils. 

reStructuredText is a revision and reinterpretation of the StructuredText and
Setext lightweight markup systems

The following documentation for RST, is pulled Text from their above website
as a demonstration of Countershape's ability to manipulate RST documents.