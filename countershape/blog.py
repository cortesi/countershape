from __future__ import with_statement
import os.path, re, datetime, urllib, codecs, functools, textwrap, tempfile, shutil
import html, model, doc, utils, template
import rssgen
import cubictemp


class Links:
    """
        A template processor for maintaining a link log. A link log is set of
        entries of the following format, separated by one or more empty line:

        http://url/
        Multiple line title

        Description that maybe multiple lines, or indeed multiple
        paragraphs.
    """
    def __init__(self, markup):
        self.markup = markup

    def parse(self, txt):
        txt = txt.expandtabs()
        txt = textwrap.dedent(txt)

        entries = []
        current = None
        whiltespace = 0
        r = re.compile(r"^\s*\n*", re.MULTILINE)
        for i in re.split(r, txt):
            si = i.strip()
            if not si:
                continue
            elif si.startswith("http://") or si.startswith("https://"):
                if current:
                    entries.append(current)
                current = {}
                parts = si.split("\n", 1)
                current["link"] = parts[0].strip()
                current["title"] = parts[1]
                current["body"] = None
            else:
                if current:
                    c = current.get("body")
                    if not c:
                        current["body"] = si
                    else:
                        current["body"] = c + "\n\n" + si
        if current:
            entries.append(current)
        return entries

    def __call__(self, str):
        parts = self.parse(str)
        links = []
        for i in parts:
            links.append(
                dict(
                    title = template.Template(self.markup, i["title"]),
                    body = template.Template(self.markup, i["body"]) if i["body"] else None,
                    link = i["link"],
                )
            )
        t = template.Template(
                self.markup,
                file(utils.data.path("resources/links.html")).read(),
                links = links
            )
        return unicode(t)


class _Postfix:
    """
        Defines a postfix added to blog posts and the index page.
    """
    def index(self, page):
        """
            Page postfix for the index page - will appear once at the bottom of
            the index page.
        """
        return ""

    def inline(self, post):
        """
            Postfix for blog posts appearing inline on a page with other posts
            (i.e. the index page). Will appear after each post.
        """
        return ""

    def solo(self, post):
        """
            Postfix for blog posts appearing alone on a page (i.e. the
            permalink destination).
        """
        return ""


class RecentPosts(_Postfix):
    TITLE = "More posts:"
    CSS_PREFIX = "recent"
    def __init__(self, num):
        self.num = num

    def _makeList(self, posts):
        monthyear = None
        output = html.DIV(_class=self.CSS_PREFIX)
        output.addChild(html.H1(self.TITLE))
        postlst = []
        for i in posts:
            postlst.append(
                html.Group(
                    html.SPAN(
                        model.LinkTo(i),
                        _class="%s-post"%self.CSS_PREFIX
                    ),
                    " ",
                    html.SPAN(
                        i.time.strftime("%d %b %Y"),
                        _class="%s-date"%self.CSS_PREFIX
                    )
                )
            )
        if postlst:
            output.addChild(html.UL(postlst))
        return output

    def index(self, idx):
        posts = idx.blog.blogdir.sortedPosts()
        return self._makeList(posts[idx.posts:idx.posts+self.num])

    def solo(self, post):
        posts = list(post.blog.blogdir.sortedPosts())
        posts.remove(post)
        return self._makeList(posts[:self.num+1])


class Disqus(_Postfix):
    def __init__(self, account):
        self.account = account

    def index(self, page):
        return html.rawstr(cubictemp.File(
            utils.data.path("resources/disqus_index.html"),
            account = self.account
        ))

    def inline(self, post):
        return html.rawstr("<a href=\"%s#disqus_thread\">Comments</a>"%model.UrlTo(post))

    def solo(self, post):
        return html.rawstr(cubictemp.File(
            utils.data.path("resources/disqus_solo.html"),
            permalink = post.permalink,
            account = self.account
        ))


class _PostRenderer(html._Renderable):
    """
        Lazy post renderer.
    """
    def __init__(self, post, *postfixes):
        """
            postfixes: A list of callables, which will be called with no
            arguments.
        """
        self.post, self.postfixes = post, postfixes
        self.src = os.path.abspath(post.src)

    def __unicode__(self):
        with utils.InDir(os.path.dirname(self.src)):
            if self.post.url:
                title = html.H1(
                    html.A(self.post.title, href=self.post.url)
                )
            else:
                title = html.H1(model.LinkTo(self.post))
            date = html.H2(self.post.time.strftime("%d %B %Y"))
            blocks = []
            blocks.append(html.DIV(title, date, _class="posthead"))
            links = Links(self.post.findAttr("markup"))
            blocks.append(html.DIV(
                       template.Template(
                            self.post.findAttr("markup"),
                            self.post.data,
                            links = links
                        ),
                       _class="postbody"
                   ))
            for i in self.postfixes:
                blocks.append(i())
            return unicode(html.DIV(*blocks, _class="post"))


class Post(doc._DocHTMLPage):
    """
        Each post is housed in a separate file, 

            First line is a multi-word title 
            Time: Time

            The rest of the file is the post. 
    """
    _TimeFmt = "%Y-%m-%d %H:%M"
    _metaRe = re.compile(r"(\w+):(.*)")
    _validOptions = set(["fullrss", "draft"])
    def __init__(self, src, blog):
        """
            :title Title of this post.
            :time DateTime object - publication time
        """
        self.blog = blog
        self.title, self.time, self.data, self.short, self.options, self.url = self.fromPath(src)
        name = os.path.basename(src) + ".html"
        doc._DocHTMLPage.__init__(
            self, name, self.title, src=src
        )
        self.changed = False
        if not self.time:
            t = self._timeToStr(datetime.datetime.now())
            self.time = self._timeFromStr(t)
            self.changed = True

    @property
    def permalink(self):
        path = [x.name for x in self.structuralPath()]
        return urllib.basejoin(self.blog.url, "/".join(path))

    @classmethod
    def _timeToStr(klass, time):
        return time.strftime(klass._TimeFmt)

    @classmethod
    def _timeFromStr(klass, txt):
        return datetime.datetime.strptime(txt.strip(), klass._TimeFmt)

    @classmethod
    def fromPath(klass, path):
        s = codecs.open(path, "r", "utf-8").read()
        return klass.fromStr(s)

    @classmethod
    def fromStr(klass, text):
        """
            Construct a post from arbitrary text.

            :text Entire text of post, including metadata.
        """
        title, time = None, None
        lines = utils.BuffIter(text.lstrip().splitlines())
        short = None
        options = set()
        url = None
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
                elif name == "url":
                    url = value.strip()
                elif name == "short":
                    v = [value]
                    for j in lines:
                        if j and not klass._metaRe.match(j.strip()):
                            v.append(j)
                        else:
                            lines.push(j)
                            short = "\n".join(v).strip()
                            break
                elif name == "options":
                    for j in value.strip().split():
                        if j in klass._validOptions:
                            options.add(j)
                        else:
                            raise ValueError("Invalid option: %s"%j)
                else:
                    raise ValueError("Invalid metadata: %s"%i)
            else:
                raise ValueError("Invalid metadata: %s"%i)
        data = "\n".join(list(lines))
        if not title:
            raise ValueError, "Not a valid post - no title found."
        return title, time, data, short, options, url

    @classmethod
    def toStr(klass, title, time, data, short, options, url):
        """
            Return a string representation of this post.
        """
        meta = [
            title,
            "time: %s"%klass._timeToStr(time),
        ]
        if short:
            meta.append("short: %s"%short)
        if options:
            meta.append("options: %s"%(",".join(options)))
        if url:
            meta.append("url: %s"%url)
        meta += [
                "",
                data
            ]
        return "\n".join(meta)

    def rewrite(self):
        # We do it this way to make sure we don't destroy data on error.
        name = tempfile.mktemp()
        f = open(name, "w")
        f.write(
            self.toStr(
                self.title,
                self.time,
                self.data,
                self.short,
                self.options,
                self.url
            )
        )
        f.close()
        shutil.move(name, self.src)

    def _prime(self, app):
        doc._DocHTMLPage._prime(self, app)
        dt = self.findAttr("contentName")
        postfixes = [functools.partial(i.solo, self) for i in self.blog.postfixes]
        self.namespace[dt] = _PostRenderer(self, *postfixes)

    def __repr__(self):
        return "Post(%s, \"%s\")"%(self.time.strftime("%d %B %Y"), self.title)


class BlogDirectory(doc.Directory):
    def __init__(self, base, src, blog):
        doc.Directory.__init__(self, base, src)
        self.blog = blog

    def defaultAction(self, src):
        src = os.path.normpath(src)
        if os.path.isdir(src):
            return BlogDirectory(os.path.basename(src), src, self.blog)
        elif not "." in os.path.basename(src):
            return Post(src, self.blog)
        else:
            return doc.Directory.defaultAction(self, src)

    def sortedPosts(self):
        lst = filter(lambda x: isinstance(x, Post), self.preOrder())
        return sorted(lst, lambda x, y: cmp(y.time, x.time))


class IndexPage(doc._DocHTMLPage):
    def __init__(self, name, title, posts, blog, *postfixes):
        doc._DocHTMLPage.__init__(self, name, title)
        self.posts, self.blog, self.postfixes = posts, blog, postfixes

    def _getIndex(self):
        out = html.Group()
        for i in self.blog.blogdir.sortedPosts()[:self.posts]:
            if "draft" in i.options:
                continue
            ps = [functools.partial(j.inline, i) for j in self.blog.postfixes]
            out.addChild(_PostRenderer(i, *ps))
        for i in self.blog.postfixes:
            out.addChild(i.index(self))
        return out

    def _getLayoutComponent(self, attr):
        if attr == self.findAttr("contentName"):
            return self._getIndex()
        else:
            return doc._DocHTMLPage._getLayoutComponent(self, attr)

    def __repr__(self):
        return "Index(%s)"%(self.title)


class ArchivePage(doc._DocHTMLPage):
    def __init__(self, name, title, blog):
        doc._DocHTMLPage.__init__(self, name, title)
        self.blog = blog

    def _getArchive(self):
        monthyear = None
        output = html.DIV(_class="archive")
        postlst = []
        for i in self.blog.blogdir.sortedPosts():
            if "draft" in i.options:
                continue
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


class RSSPage(model.BasePage, doc._DocMixin):
    structural = False
    NUM = 10
    def __init__(self, name, title, posts, blog):
        self.name, self.title, self.posts = name, title, posts
        self.blog = blog
        self.src = "."
        model.BasePage.__init__(self)

    def _getRSS(self):
        items = []
        for i in self.blog.blogdir.sortedPosts()[:self.NUM]:
            if "draft" in i.options:
                continue
            path = [x.name for x in i.structuralPath()]
            if ("fullrss" in i.options) or i.url:
                r = _PostRenderer(i)
                description = unicode(r)
            else:
                description = i.short or i.title
            items.append(
                rssgen.RSSItem(
                    title = i.title,
                    description = description,
                    link = i.url or i.permalink,
                    guid = rssgen.Guid(i.permalink),
                    pubDate = i.time
                )
            )
        rss = rssgen.RSS2(
            title = self.blog.blogname,
            link = self.blog.url,
            description = self.blog.blogdesc,
            items = items
        )
        return rss.to_xml()

    def __repr__(self):
        return "RSS(%s)"%self.name

    def __call__(self, *args, **kwargs):
        yield self._getRSS()


class Blog:
    def __init__(self, blogname, blogdesc, url, base, src, *postfixes):
        """
            postfixes: A set of Postfix objects, which will be appended in the
            relevant places in the specified order.
        """
        src = os.path.abspath(src)
        self.blogname, self.url, self.base, self.src = blogname, url, base, src
        self.blogdesc = blogdesc
        self.postfixes = postfixes
        if not os.path.isdir(src):
            raise model.ApplicationError("Blog source is not a directory: %s"%src)
        self.blogdir = BlogDirectory(base, src, self)

    def index(self, name, title, posts=10):
        return IndexPage(name, title, posts, self, *self.postfixes)
        
    def archive(self, name, title):
        return ArchivePage(name, title, self)

    def rss(self, name, title, posts=10):
        return RSSPage(
            name,
            title,
            posts,
            self
        )

    def __call__(self):
        return self.blogdir
