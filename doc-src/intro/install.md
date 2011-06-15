## Dependencies

### TinyTree

<!--(block | syntax("bash"))-->
$ git clone git://github.com/cortesi/tinytree.git
$ cd tinytree
$ sudo setup.py install
<!--(end)-->

### Cubictemp

<!--(block | syntax("bash"))-->
$ git clone git://github.com/cortesi/cubictemp.git
$ cd cubictemp
$ sudo setup.py install
<!--(end)-->

## Optional

### Text Markup Tools

#### DOCUTILS

[DOCUTILS Project Site](http://docutils.sourceforge.net)

<blockquote>
Docutils is an open-source text processing system for processing plaintext 
documentation into useful formats, such as HTML or LaTeX. It includes reStructuredText, 
the easy to read, easy to use, what-you-see-is-what-you-get plaintext markup language.
</blockquote>

Download the current version of the docutils from the [Project Site](http://docutils.sourceforge.net)

<!--(block | syntax("bash"))-->
$ tar -zxf docutils-0.7.tgz
$ cd docutils
$ sudo python setup.py install
<!--(end)-->


#### MARKDOWN

<blockquote>
Markdown is a light text markup format and a processor to convert that to HTML. 
The originator describes it as follows: 

Markdown is a text-to-HTML conversion tool for web writers. Markdown allows you 
to write using an easy-to-read, easy-to-write plain text format, then convert it 
to structurally valid XHTML (or HTML). 
</blockquote>

<!--(block | syntax("bash"))-->
$ git clone https://github.com/trentm/python-markdown2.git
$ cd python-markdown2
$ sudo setup.py install
<!--(end)-->

### Syntax Highlighting

Pygments

<blockquote>
is a generic syntax highlighter for general use in all kinds of software 
such as forum systems, wikis or other applications that need to prettify 
source code.</blockquote>

Refer to the [project page](http://pygments.org) for getting pygments.

<!--(block | syntax("bash"))-->
$ sudo easy_install Pygments 
<!--(end)-->

After installing Pygments, generate the CSS Style Sheet to be used in
your site using the following:

<!--(block | syntax("bash"))-->
$ pygmentize -S default -f html -a ".highlight" > syntax.css
<!--(end)-->

### Test Suite

