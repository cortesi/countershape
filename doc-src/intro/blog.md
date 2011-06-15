# Blogging with Countershape

Countershape provides a number of tools to assist with
static site generated web logs.

-   Write It
-   Configure It
-   Metadata

## Write It

## Configure It

Configuring your blog is as simple as the following example:

<pre>
base-dir+
        | site-src
        | blog-posts
</pre>

file: base-dir/site-src/index.py

<!--(block | cubescript | syntax("py"))-->
$!readFrom("../examples/myblog/site-src/index.py")!$
<!--(end)-->




## Metadata

To help your readers, and Search Engine Optimisation (SEO) Blogs
generally supply a number of metadata selectively added by 
blog entry/article writers.

To include a supported metadata in your blog 
Standard metadata for Blogs, are grouped together at the 
beginning of your post, and (a) begin the newline, (b) delineated
with a colon ":"

For example:

File: Post-Random

<pre>
The first line can be anything, and becomes my title
time: 2012-12-01 14:22

Metadata begins the line with the keyword, followed by a colon ":"

Content is anything that's not metadata, but does look cleaner when
separated by a blank line ?

</pre>

Metadata supported by Countershape include:

<table>
    <tr><th>Metadata</th>
        <th>Description</th>
    </tr><tr>
        <td>Title</td>
        <td>(required) The first line of any post/article is taken as the
        title.</td>
    </tr><tr>
        <td>Time</td>
        <td>(optional) the time for the entry in the format YYYY-MM-DD HH:MM
    If the metadata is not specified, then it will be automatically generated for you.</td>
    </tr><tr>
        <td>URL</td>
        <td>(optional) </td>
    </tr><tr>
        <td>Short</td>
        <td>(optional) A short description (brief) of the article</td>
    </tr><tr>
        <td>Options</td>
        <td>(optional) Can be any of the following: fullrss, draft, top
        <ul>
            <li>fullrss - override site settings for RSS and generate body text with the RSS xml.</li>
            <li>draft - post is not rendered into site html</li>
            <li>top - used by blog.RecentPosts when showing recent "top" posts.</li>
        </ul>
        </td>
    </tr><tr>
        <td>Tags</td>
        <td>(optional) A comma separated list of Tags</td>
    </tr>
</table>
