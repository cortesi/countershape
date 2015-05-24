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
        <td>Define the markdown class to use in rendering html from source file.
<!--(block | syntax("py"))-->
this.markup = markup.Markdown(extras=["code-friendly"])
<!--(end)-->
        </td>
    </tr>
    <tr><td>contentName</td>
        <td>blog, doc</td>
        <td>Used internally for specifying Document Text for rendering page components.
<!--(block | syntax("py"))-->
<!--(end)-->
        </td>
    </tr>
    <tr><td>absolute_domain</td>
        <td>model</td>
        <td>Specify the base Domain to use for site level URL references.
<!--(block | syntax("py"))-->
this.absolute_domain="www.example.com"
<!--(end)-->
        </td>
    </tr>
    <tr><td>site_url</td>
        <td>model</td>
        <td>Specify the base site URL to use for site level URL references.
<!--(block | syntax("py"))-->
this.site_url="www.example.com"
<!--(end)-->
        </td>
    </tr>
    <tr><td>layout</td>
        <td>model</td>
        <td>Specify the layout.Layout for rendering a page.
<!--(block | syntax("py"))-->
this.layout = countershape.Layout("_layout.html")
<!--(end)-->
        </td>
    </tr>
    <tr><td>stdHeaders</td>
        <td>model</td>
        <td>Used to refer to filenames parsed by Countershape to specify the 
        appropriate &lt;link  href="../media/css/docstyle-default.css" type="text/css" rel="StyleSheet"/>. Supports:
        
        <ul>
            <li>.js - Javascript </li>
            <li>.css - CSS Stylesheet</li>
        </ul>
<!--(block | syntax("py"))-->
this.stdHeaders = [
    widgets.UrlTo("media/css/syntax.css"),
    widgets.UrlTo("media/js/menu.js"),
]
<!--(end)-->
        </td>
    </tr>
    <tr><td>titlePrefix</td>
        <td>doc</td>
        <td>Used in HTML Page Rendering to specify the
        Page Title. titlePrefix is prepended to the Page pageTitle
        to Generate the eventual "&lt;title> $titlePrefix + $pageTitle </title>
<!--(block | syntax("py"))-->
this.titlePrefix = "Countershape "
pages = [
    Page(
        name="markup/markup.md", 
        title="Page Markup",
        pageTitle="Page Markup Options"
        ),
]
<!--(end)-->

        The above example will generate the Page Title:
        
        &lt;title>Countershape Page Markup Options</title>
        </td>
    </tr>
</table>


Example index.py

<!--(block | syntax("py"))-->
import countershape
from countershape import Page, Directory, PythonModule, markup
from countershape.doc import *
          
this.markup = markup.Markdown(extras=["code-friendly"])

this.layout = countershape.Layout( path="_layout.html" )
this.titlePrefix = "Countershape "

this.stdHeaders = [
    widgets.UrlTo("media/css/syntax.css"),
]
<!--(end)-->

## Pages

Everything is a page ?

After reading the configuration file (index.py) the "pages" list
is used for:

- Creating a table of content
- Executing files/paths to be "processed"

<!--(block | syntax("py"))-->
pages = [
    Page(
        name="markup/markup.md", 
        title="Page Markup",
        pageTitle="Page Markup Options"
        ),
    Directory("markup"),
    
    PythonModule(
        name="../countershape", 
        title="Source"),
]
<!--(end)-->

### doc.Page

A document page (doc.Page) processes files specified in
the parameters.

-   title - Used in item-list of contents linked to
    through the configuration file.
-   name - The file to be processed
-   pageTitle - Used in the Page rendered Title

Note: If the file _src_ is not in the configuration (index.py) directory, the generated
HTML file will be generated into this directory. Name conflicts will occur if you are not
careful of this.

### doc.Directory

A directory that has it's own configuration file (index.py) for configuring the
contents of that directory.

### doc.PythonModule

Parse the name=Directory for Python files and generate HTML syntax highlighted
pages from them.

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