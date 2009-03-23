from __future__ import with_statement
import os.path, re, datetime, urllib
import html, model, doc, utils, template
import rssgen

class _PostRenderer(html._Renderable):
    """
        Lazy post renderer.
    """
    def __init__(self, post, markup):
        self.post, self.markup = post, markup
        self.src = os.path.abspath(post.src)
    
    def __str__(self):
        with utils.InDir(os.path.dirname(self.src)):
            title = html.H1(model.LinkTo(self.post))
            date = html.H2(self.post.time.strftime("%d %B %Y"))
            head = html.DIV(title, date, _class="posthead")
            body = html.DIV(
                       template.Template(self.markup, self.post.data),
                       _class="postbody"
                   )
            return str(html.DIV(head, body, _class="post"))


class Post(doc._DocHTMLPage):
    """
        Each post is housed in a separate file, 

            First line is a multi-word title 
            Time: Time

            The rest of the file is the post. 
    """
    _TimeFmt = "%Y-%m-%d %H:%M"
    _metaRe = re.compile(r"(\w+):(.*)")
    def __init__(self, src):
        """
            :title Title of this post.
            :time DateTime object - publication time
        """
        self.title, self.time, self.data, self.short = self.fromPath(src)
        name = os.path.basename(src) + ".html"
        doc._DocHTMLPage.__init__(
            self, name, self.title, src=src
        )
        self.changed = False
        if not self.time:
            t = self._timeToStr(datetime.datetime.now())
            self.time = self._timeFromStr(t)
            self.changed = True

    @classmethod
    def _timeToStr(klass, time):
        return time.strftime(klass._TimeFmt)

    @classmethod
    def _timeFromStr(klass, txt):
        return datetime.datetime.strptime(txt.strip(), klass._TimeFmt)

    @classmethod
    def fromPath(klass, path):
        s = file(path).read()
        return klass.fromStr(s)

    @classmethod
    def fromStr(klass, text):
        """
            Construct a post from arbitrary text.

            :text Entire text of post, including metadata.
        """
        title, time = None, None
        lines = iter(text.lstrip().splitlines())
        short = None
        for i in lines:
            i = i.strip()
            if not i:
                break
            if not title:
                title = i
                continue
            match = klass._metaRe.match(i)
            if match:
                name = match.group(1).lower()
                value = match.group(2)
                if name == "time":
                    time = klass._timeFromStr(value)
                elif name == "short":
                    v = [value]
                    for i in lines:
                        if i:
                            v.append(i)
                        else:
                            short = "\n".join(v).strip()
                            break
                    break
                else:
                    raise ValueError("Invalid metadata: %s"%i)
            else:
                raise ValueError("Invalid metadata: %s"%i)
        data = "\n".join(list(lines))
        if not title:
            raise ValueError, "Not a valid post - no title found."
        return title, time, data, short

    def toStr(self):
        """
            Return a string representation of this post.
        """
        meta = [
            self.title,
            "time: %s"%self._timeToStr(self.time),
        ]
        if self.short:
            meta.append("short: %s"%self.short)
        meta += [
                "",
                self.data
            ]
        return "\n".join(meta)

    def rewrite(self):
        f = open(self.src, "w")
        f.write(self.toStr())

    def _prime(self, app):
        doc._DocHTMLPage._prime(self, app)
        dt = self.findAttr("contentName")
        self.namespace[dt] = _PostRenderer(self, self.findAttr("markup"))

    def __repr__(self):
        return "Post(%s, \"%s\")"%(self.time.strftime("%d %B %Y"), self.title)


class BlogDirectory(doc.Directory):
    def defaultAction(self, src):
        src = os.path.normpath(src)
        if os.path.isdir(src):
            return BlogDirectory(os.path.basename(src), src)
        elif not "." in os.path.basename(src):
            return Post(src)
        else:
            return doc.Directory.defaultAction(self, src)

    def sortedPosts(self):
        lst = filter(lambda x: isinstance(x, Post), self.preOrder())
        return sorted(lst, lambda x, y: cmp(y.time, x.time))


class IndexPage(doc._DocHTMLPage):
    def __init__(self, name, title, blogdir, posts):
        doc._DocHTMLPage.__init__(self, name, title)
        self.blogdir, self.posts = blogdir, posts

    def _getIndex(self):
        out = html.Group()
        for i in self.blogdir.sortedPosts()[:self.posts]:
            out.addChild(_PostRenderer(i, self.findAttr("markup")))
        return out

    def _getLayoutComponent(self, attr):
        if attr == self.findAttr("contentName"):
            return self._getIndex()
        else:
            return doc._DocHTMLPage._getLayoutComponent(self, attr)

    def __repr__(self):
        return "Index(%s)"%(self.title)


class ArchivePage(doc._DocHTMLPage):
    def __init__(self, name, title, blogdir):
        doc._DocHTMLPage.__init__(self, name, title)
        self.blogdir = blogdir

    def _getArchive(self):
        monthyear = None
        output = html.DIV(_class="archive")
        postlst = []
        for i in self.blogdir.sortedPosts():
            my = i.time.strftime("%B %Y")
            if my != monthyear:
                if postlst:
                    output.addChild(html.UL(postlst))
                    postlst = []
                monthyear = my
                output.addChild(html.H1(monthyear))
            postlst.append(
                html.Group(
                    html.SPAN(model.LinkTo(i), _class="archive-post"),
                    " ",
                    html.SPAN(i.time.strftime("%d %b %Y"), _class="archive-date")
                )
            )
        if postlst:
            output.addChild(html.UL(postlst))
        return output

    def _getLayoutComponent(self, attr):
        if attr == self.findAttr("contentName"):
            return self._getArchive()
        else:
            return doc._DocHTMLPage._getLayoutComponent(self, attr)

    def __repr__(self):
        return "Archive(%s)"%(self.title)


class RSSPage(model.Page, doc._DocMixin):
    structural = False
    def __init__(self, name, title, blogdir, posts, blogname, description, url):
        self.name, self.title = name, title
        self.blogdir, self.posts, self.blogname = blogdir, posts, blogname
        self.description, self.url = description, url
        self.src = "."
        model.Page.__init__(self)

    def _getRSS(self):
        items = []
        for i in self.blogdir.sortedPosts()[:10]:
            path = [x.name for x in i.structuralPath()]
            link = urllib.basejoin(self.url, "/".join(path))
            items.append(
                rssgen.RSSItem(
                    title = i.title,
                    description = i.short or i.data,
                    link = link,
                    guid = rssgen.Guid(link),
                    pubDate = i.time
                )
            )
        rss = rssgen.RSS2(
            title = self.blogname,
            link = self.url,
            description = self.description,
            items = items
        )
        return rss.to_xml()

    def __repr__(self):
        return "RSS(%s)"%self.name

    def __call__(self, *args, **kwargs):
        yield self._getRSS()


class Blog:
    def __init__(self, blogname, blogdesc, url, base, src):
        src = os.path.abspath(src)
        self.blogname, self.url, self.base, self.src = blogname, url, base, src
        self.blogdesc = blogdesc
        if not os.path.isdir(src):
            raise model.ApplicationError("Blog source is not a directory: %s"%src)
        self.blogdir = BlogDirectory(base, src)

    def index(self, name, title, posts=10):
        return IndexPage(name, title, self.blogdir, posts)
        
    def archive(self, name, title):
        return ArchivePage(name, title, self.blogdir)

    def rss(self, name, title, posts=10):
        return RSSPage(
            name,
            title,
            self.blogdir,
            posts,
            self.blogname,
            self.blogdesc,
            self.url
        )

    def __call__(self):
        return self.blogdir
