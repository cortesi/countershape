# Site Configuration Wide Settings

Configuration settings for files in a path are stored in the
python script "index.py" The settings in the file will apply
to all files in that directory, and following directories unless
overridden by another configuration file (index.py.)

index.py is a standard Python file loaded into countershape at
the point of traversing your directory structure.

## Global Settings

Specify Global Attributes using the special indexer 'this' such as in:

<pre class="config-file">
this.markup = markup.Markdown()
</pre>

<table>
    <tr><th>Attribute</th>
        <th>Module</th>
        <th>Use</th>
    </tr>
    <tr><td>markup</td>
        <td>blog, doc, model</td>
        <td>Define the markdown class to use in rendering html from source file.</td>
    </tr>
    <tr><td>contentName</td>
        <td>blog, doc</td>
        <td>Used internally for specifying Document Type for rendering page components.</td>
    </tr>
    <tr><td>absolute_domain</td>
        <td>model</td>
        <td>Specify the base Domain to use for site level URL references.</td>
    </tr>
    <tr><td>site_url</td>
        <td>model</td>
        <td>Specify the base site URL to use for site level URL references.</td>
    </tr>
    <tr><td>layout</td>
        <td>model</td>
        <td>Specify the layout.Layout for rendering a page.</td>
    </tr>
</table>

- stdHeaders
- titlePrefix

Example index.py

<!--(block | syntax("py"))-->
import countershape
from countershape import Page, Directory, PythonModule, markup
from countershape.doc import *
          
this.markup = markup.Markdown(extras=["code-friendly"])

this.layout = countershape.Layout("_layout.html")
this.titlePrefix = "Countershape "

this.stdHeaders = [
    model.UrlTo("media/css/reset-fonts-grids-base.css"),
    model.UrlTo("media/css/docstyle-default.css"),
    model.UrlTo("media/css/docstyle-customised.css"),
    model.UrlTo("media/css/syntax.css"),
]
<!--(end)-->

## Pages

Everything is a page ?

<!--(block | syntax("py"))-->
pages = [
    Page("markup/markup.md", 
        title="Page Markup",
        pageTitle="Page Markup Options"
        ),
    Directory("markup"),
    
    PythonModule("../countershape", 
        title="Source"),
]

<!--(end)-->

## Namespaces

Your site can use a private namespace to store functions, macros
you wish to use within the generation of web pages. Some
namespaces provided with the system are:

<table>
    <tr><th>class</th>
        <th>namespace</th>
    </tr><tr>
        <td>blog.RSSPage</td>
        <td>syntax, readFrom</td>
    </tr><tr>
        <td>doc.DocRoot</td>
        <td>syntax, readFrom, options</td>
    </tr><tr>
        <td></td>
        <td></td>
    </tr><tr>
        <td></td>
        <td></td>
    </tr><tr>
        <td></td>
        <td></td>
    </tr><tr>
        <td></td>
        <td></td>
    </tr><tr>
        <td></td>
        <td></td>
    </tr>
</table>

## Template