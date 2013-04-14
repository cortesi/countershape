"""
    This module provides a high-level framework for web applications.
"""
import os.path, sys, cStringIO, inspect, types, copy, datetime
import mimetypes, time
import cubictemp, tinytree
import countershape, html, layout
import utils, state


class ApplicationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.page = state.page


class UrlTo:
    """
        A lazily evaluated URL to a page in this application.
    """
    _cubictemp_unescaped = True
    def __init__(self, pageSpec, anchor=None):
        """
            :pageSpec A Countershape page specification
            :anchor Anchor to add to URL
        """
        self.pageSpec = pageSpec
        self.anchor = anchor

    def __str__(self):
        to = state.application.getPage(self.pageSpec)
        if not to:
            s = "Link to unknown page: %s."%self.pageSpec
            raise ApplicationError(s)
        if to.internal:
            s = "URL request to internal page: %s."%to.name
            raise ApplicationError(s)

        absdomain = state.page.findAttr("absolute_domain", None)
        if absdomain:
            u = to.absolutePath()
            u = utils.urlCat(to.siteUrl(), u)
        else:
            rel = state.page.relativePath([i.name for i in to.structuralPath()])
            u = utils.makeURL(rel)

        if self.anchor:
            u = u + "#%s"%self.anchor
        return u


class Link(html._Renderable):
    """
        A standard href link.
    """
    def __init__(self, destination):
        """
            The arguments are as follows:

                destination         Link destination (optional)
        """
        html._Renderable.__init__(self)
        self.destination = destination

    def __call__(self, valobj=None, **kwargs):
        return html._Renderable.__call__(self, valobj, **kwargs)

    def __str__(self):
        content = self.page.title or self.page.name
        vals = {}
        url = UrlTo(self.destination, **vals)
        return unicode(html.A(content, href=url))


class ALink(html._Renderable):
    """
        Lazy simple A HREF link.
    """
    _cubictemp_unescaped = 1
    def __init__(self, page, txt, anchor=None):
        self.page, self.txt, self.anchor = page, txt, anchor
        html._Renderable.__init__(self)

    def __str__(self):
        url = UrlTo(self.page, anchor=self.anchor)
        return unicode(html.A(self.txt, href=url))


class LinkTo(html._Renderable):
    """
        A lazily evaluated link to a page in this application, created using
        the _link_ attribute for the destination page.
    """
    _cubictemp_unescaped = True
    def __init__(self, page):
        """
            :page Page specification
        """
        html._Renderable.__init__(self)
        self.page = page

    def _getLink(self):
        p = state.application.getPage(self.page)
        if not p:
            s = "Link to unknown page: %s."%self.page
            raise ApplicationError(s)
        l = p.link()
        l.page = p
        return l

    def __call__(self):
        """
            This method complies with the _Renderable interface, although we
            don't return a LinkTo object - we return the link object itself.
        """
        return self._getLink()

    def __str__(self):
        return unicode(self._getLink())


class Top:
    """
        Lazy URL to top of site.
    """
    def __str__(self):
        return utils.urlCat("./", state.page.top())


class BasePage(tinytree.Tree):
    """
        Objects inheriting from this class should over-ride the run() method,
        which will be called with the arguments of the page submission as
        keywords.
    """
    # Name of page (possibly not unique)
    name = None
    # Name of page presented in menus, etc.
    title = None
    # Is this page at the root of the application tree?
    root = False
    # True if page is not directly callable
    internal = False
    # True if page will appear in the site indexes and menus
    structural = False
    # Set to an absolute path if the page has a source file
    src = None
    def __init__(self, children = None):
        if state.page and not state.application.testing:
            raise ApplicationError(
                    "Page object instantiated during page call. Last page: %s"%state.page.name
                )
        tinytree.Tree.__init__(self, children)
        if not self.name:
            self.name = self.__class__.__name__
        self.link = Link(self)

    def _prime(self, app):
        """
            Prime the page for use after constructing the page tree.
        """
        self.application = app
        sp = self.structuralPath()
        self.path = os.path.sep + (os.path.sep).join([i.name for i in sp])

    def under(self, path):
        p = state.application.getPage(path)
        if p == self:
            return True
        return self.isDocDescendantOf(p)

    def structuralPath(self):
        """
            Retrieve a list of structural pages that lie on the path from the
            root to the current page, including the current page.
        """
        p = [i for i in self.pathToRoot() if i.structural]
        p.reverse()
        if self.parent:
            if not p or (not (p[-1] is self)):
                p.append(self)
        return p

    def reset(self):
        """
            Reset page state. Called just before a page is called.
        """
        pass

    def match(self, path, exact):
        """
            Walk up the tree to see if we match the specified path.

            path:   A list of path elements, or a string path specification.

        """
        if isinstance(path, basestring):
            path = [i for i in path.split(os.path.sep) if i]
        sp = self.structuralPath()
        for j in reversed(path):
            if not sp:
                return False
            if not j == sp.pop().name:
                return False
        if sp and exact:
            return False
        return True

    def top(self):
        l = len(self.structuralPath()) - 1
        return (os.path.sep).join([".."]*l)

    def absolutePath(self):
        p = [i.name for i in self.structuralPath()]
        return utils.urlCat(*p)

    def relativePath(self, toPath):
        """
            Return a relative path to a page specified by a list of path
            components. The argument should be a full path relative to the root
            of this application.
        """
        common = 0
        fromPath = [i.name for i in self.structuralPath()]
        for common, e in enumerate(zip(fromPath, toPath)):
            if not e[0] == e[1]:
                break
        backtrack = [".."]*((len(fromPath) - 1)-common)
        return utils.urlCat(*(backtrack + toPath[common:]))

    def isDocDescendantOf(self, other):
        """
            Check if this page is a document index descendant of other. This is
            like "isDescendantOf" in tinytree, but includes adjacent internal
            pages and their descendants.
        """
        if other.isDescendantOf(self):
            return True
        elif other.getNext() in other.siblings() and other.getNext().internal:
            return other.getNext().isDescendantOf(self)
        else:
            return False

    def render(self):
        try:
            bod=[unicode(i) for i in self.run()]
        except UnicodeEncodeError:
            bod=[unicode(str(i),'latin-1', 'ignore') for i in self.run()]
        return "".join(bod)

    def siteUrl(self):
        r = self.findAttr("site_url")
        if not r:
            raise ApplicationError("Requires a site URL.")
        return r

    def lastMod(self):
        """
            Returns a datetime object for the last file modification.
        """
        if not self.src:
            return None
        return datetime.datetime.fromtimestamp(os.path.getmtime(self.src))

    def __repr__(self):
        return "Page(%s)"%self.name


class Header(object):
    def __init__(self, page):
        self.page = page
        self._jsPath = utils.OrderedSet()
        self._cssPath = utils.OrderedSet()
        self._metaData = utils.OrderedSet()

    def jsPath(self, path, **attrs):
        self._jsPath.append(
            unicode(html.SCRIPT(src=path, type="text/javascript", **attrs))
        )

    def cssPath(self, path, **attrs):
        self._cssPath.append(
            unicode(html.LINK(rel="StyleSheet", href=path, type="text/css", **attrs))
        )
    def metaData(self, key, value):
        self._metaData.append(
            unicode("<META %s=\"%s\">" % (key.upper(), value) )
        )
    def path(self, spec):
        path = unicode(spec)
        if path.endswith(".css"):
            self.cssPath(path)
        elif path.endswith(".js"):
            self.jsPath(path)
        else:
            s = "Unrecognised resource extension (neither .css nor .js)."
            raise ValueError, s

    def __str__(self):
        sofar = set()
        adds = []
        for i in list(self.page.attrsToRoot("stdHeaders")):
            thispage = []
            for j in i:
                _, base = os.path.split(j.pageSpec)
                if not base in sofar:
                    thispage.append(j)
                    sofar.add(base)
            adds.extend(reversed(thispage))
        meta = self.page.findAttr("metadata")
        if meta != None:
            for k, v in meta.iteritems():
                self.metaData(k, v)

        for i in reversed(adds):
            self.path(i)
        return "\n".join(
                    [
                        "\n",
                        unicode(self._metaData),
                        unicode(self._cssPath),
                        unicode(self._jsPath),
                    ]
                )


class HTMLPage(BasePage):
    """
        Instances of this class represent HTML pages. Children of this class
        would normally over-ride a suite of methods that depend on the
        particular layout object chosen for the class.
    """
    defaultLayout = layout.Layout()
    structural = True
    def pageTitle(self, *args, **kwargs):
        return self.title or self.name

    def reset(self):
        self.header = Header(self)

    def _getLayoutComponent(self, attr, *args, **kwargs):
        """
            Component retrieval method.

                - Find an attribute of the right name - if the attribute is a
                  string, return it. If it is a callable, call it with the
                  supplied arguments.
        """
        meth = self.findAttr(attr)
        if meth is None:
            s = "Cannot find layout component \"%s\""%attr
            raise ApplicationError(s)
        if callable(meth):
            ret = meth(*args, **kwargs)
            if isinstance(ret, types.GeneratorType):
                # List-ify it now, to make tracking down evaluation errors
                # easier.
                lst = list(ret)
                return html.Group(*lst)
            else:
                return ret
        else:
            return meth

    def render(self):
        layout = self.findAttr("layout", self.defaultLayout)
        return unicode(layout(self))

    def __repr__(self):
        return "HTMLPage(%s)"%self.name


class BaseRoot(BasePage):
    root = True


class BaseApplication(object):
    testing = 0
    def __init__(self, root):
        """
            Takes the root node of a tree of pages.
        """
        self.root = root
        self._pages = {}
        for i in root.preOrder():
            self.addPage(i)

    def getPage(self, page):
        """
            :page Either a page object, or a string path specification.

            Find a page specified using minimally unique path information. Note
            that the path used is the _structural_ path - non-structural pages
            are not taken into account.

            Examples:

                /foo       - A node named "foo" on the structural root.

                foo        - Any node named "foo". If there is more than one, this
                             will raise an Ambiguous Link error.

                ./foo      - A descendant of the current page named foo.

                ^/foo      - An ancestor of the current page named foo.

                -/foo      - A sibling of the current page named foo.

                $/foo      - A page in the same subtree as the current page.
                             This means that the page is either a descendant,
                             or a sibling or an ancestor of the current page.
        """
        return self.getPageFrom(state.page, page)

    def getPageFrom(self, fromPage, toPage):
        if isinstance(toPage, BasePage):
            return toPage
        elif utils.isStringLike(toPage):
            exact, isParent, isChild, isSibling, isLocal = False, False, False, False, False
            if toPage.startswith("/") or toPage.startswith(os.path.sep):
                exact = True
            elif toPage.startswith("./") or toPage.startswith("." + os.path.sep):
                isChild = True
                toPage = toPage[2:]
            elif toPage.startswith("^/") or toPage.startswith("^" + os.path.sep):
                isParent = True
                toPage = toPage[2:]
            elif toPage.startswith("-/") or toPage.startswith("-" + os.path.sep):
                isSibling = True
                toPage = toPage[2:]
            elif toPage.startswith("$/") or toPage.startswith("$" + os.path.sep):
                isLocal = True
                toPage = toPage[2:]
            if any([isParent, isChild, isSibling, isLocal]) and not fromPage:
                s = "Relative page link '%s' outside of page call context."%toPage
                raise ApplicationError(s)
            path = [i for i in os.path.normpath(toPage).split(os.path.sep) if i and i != "."]
            if not path:
                return self.root
            pname = path[-1]
            pagelist = self._pages.get(pname, None)
            if pagelist:
                match = None
                for p in pagelist:
                    if isChild:
                        if not fromPage.isDescendantOf(p):
                            continue
                    elif isParent:
                        if not p.isDescendantOf(fromPage):
                            continue
                    elif isSibling:
                        if not fromPage.isSiblingOf(p):
                            continue
                    elif isLocal:
                        values = [
                            fromPage.isDescendantOf(p),
                            p.isDescendantOf(fromPage),
                            fromPage.isSiblingOf(p)
                        ]
                        if not any(values):
                            continue
                    if p.match(path, exact):
                        if match:
                            raise ApplicationError(
                                    "Ambiguous path specification: %s."%toPage
                            )
                        match = p
                return match
            else:
                return None
        else:
            s = "Invalid argument to getPage: %s."%repr(toPage) +\
                " Must be either a string or a Page object."
            raise ApplicationError(s)

    def getPath(self, path):
        """
            path        :   A list of path elements.

            Returns a callable object corresponding to the named page, and a
            tuple which is the path "remainder". So, a request for /foo/bar/woo
            would result in a path argument of ["foo", "bar", "woo"]. If this
            matches a page "foo", the remainder will be ["bar", "woo"].

            Always returns a page, or raises an error.
        """
        l = len(path)
        for i in range(l):
            match = self._pages.get(path[-i-1])
            if match:
                p = os.path.sep + (os.path.sep).join(path[:l-i])
                for j in match:
                    if not j.internal and j.path == p:
                        return j, path[l-i:]
        return self.root, path

    def addPage(self, page):
        page._prime(self)
        lst = self._pages.setdefault(page.name, [])
        for i in lst:
            if i.path == page.path:
                e = "Ambiguous page structure: duplicate page %s."
                raise ApplicationError(e%(page.path))
        lst.append(page)

    def pre(self, p):
        stateVals = [
            state.page,
            state.application,
        ]
        if (not self.testing) and any(stateVals):
            vals = [
                "state.page : %s"%state.page,
                "state.application : %s"%state.application,
            ]
            s = "Dirty state: (%s)"%(" ;".join(vals))
            raise ApplicationError(s)
        if not self.testing:
            self._resetState()
        state.page = p
        state.application = self
        p.reset()

    def _resetState(self):
        state.page = None
        state.application = None

    def post(self, p):
        self._resetState()

    def __call__(self, page):
        self.pre(page)
        d = page.render()
        self.post(page)
        return d

