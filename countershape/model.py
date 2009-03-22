"""
    This module provides a high-level framework for web applications.
"""
import os.path, sys, cStringIO, inspect, types, copy
import mimetypes, time
import cubictemp, tinytree
import countershape, html, layout, template, form, encoding
import utils, state


class ApplicationError(Exception): pass


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
            raise countershape.ApplicationError(s)
        if to.internal:
            s = "URL request to internal page: %s."%to.name
            raise countershape.ApplicationError(s)
        rel = state.page.relativePath([i.name for i in to.structuralPath()])
        u = utils.makeURL(rel)
        if self.anchor:
            u = u + "#%s"%self.anchor
        return u


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
            raise countershape.ApplicationError(s)
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


class Top:
    """
        Lazy URL to top of site.
    """
    def __str__(self):
        return utils.urlCat("./", state.page.top())


class Page(tinytree.Tree):
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
    def __init__(self, children = None):
        if state.page and not state.application.testing:
            raise ApplicationError("Page object instantiated during page call.")
        tinytree.Tree.__init__(self, children)
        if not self.name:
            self.name = self.__class__.__name__
        self.link = form.Link(self)

    def _prime(self, app):
        """
            Prime the page for use after constructing the page tree.
        """
        self.application = app
        sp = self.structuralPath()
        self.path = "/" + "/".join([i.name for i in sp])

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

    def matchPage(self, path, exact):
        """
            Walk up the tree to see if we match the specified path.

            path    :   A list of path elements, NOT including the name of the
            current page. I.e. for a path foo/bar, this function would be
            called on the page named "bar" with path argument ["foo"].
        """
        sp = self.structuralPath()[:-1]
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
        return "/".join([".."]*l)

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

    def __call__(self):
        bod = [unicode(i) for i in self.run()]
        yield "".join(bod)

    def __repr__(self):
        return "Page(%s)"%self.name


class Header(object):
    def __init__(self, page):
        self.page = page
        self._js = utils.OrderedSet()
        self._css = utils.OrderedSet()
        self._jsPath = utils.OrderedSet()
        self._cssPath = utils.OrderedSet()

    def jsPath(self, path, **attrs):
        self._jsPath.append(
            unicode(html.SCRIPT(src=path, type="text/javascript", **attrs))
        )

    def cssPath(self, path, **attrs):
        self._cssPath.append(
            unicode(html.LINK(rel="StyleSheet", href=path, type="text/css", **attrs))
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
        for i in reversed(list(self.page.attrsToRoot("stdHeaders"))):
            for j in i:
                self.path(j)
        return "\n".join(
                    [
                        unicode(self._cssPath),
                        unicode(self._css),
                        unicode(self._jsPath),
                        unicode(self._js),
                    ]
                )


class HTMLPage(Page):
    """
        Instances of this class represent HTML pages. Children of this class
        would normally over-ride a suite of methods that depend on the
        particular layout object chosen for the class.
    """
    defaultLayout = layout.Layout()
    structural = True
    selfcontained = False
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
            raise countershape.ApplicationError(s)
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

    def __call__(self):
        layout = self.findAttr("layout", self.defaultLayout)
        yield unicode(layout(self))

    def __repr__(self):
        return "HTMLPage(%s)"%self.name


class BaseRoot(Page):
    root = True
    def getFirst(self):
        for i in self.preOrder():
            return i


class AppRoot(BaseRoot):
    def __init__(self, *args, **kwargs):
        BaseRoot.__init__(self, *args, **kwargs)
        self.first = self.getFirst()

    def run(self):
        return "test"


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
        if isinstance(toPage, Page):
            return toPage
        elif utils.isStringLike(toPage):
            exact, isParent, isChild, isSibling, isLocal = False, False, False, False, False
            if toPage.startswith("/"):
                exact = True
            elif toPage.startswith("./"):
                isChild = True
                toPage = toPage[2:]
            elif toPage.startswith("^/"):
                isParent = True
                toPage = toPage[2:]
            elif toPage.startswith("-/"):
                isSibling = True
                toPage = toPage[2:]
            elif toPage.startswith("$/"):
                isLocal = True
                toPage = toPage[2:]
            if any([isParent, isChild, isSibling, isLocal]) and not fromPage:
                s = "Relative page link '%s' outside of page call context."%toPage
                raise ApplicationError(s)
            path = [i for i in toPage.split("/") if i]
            if not path:
                return self.root
            pname = path.pop()
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
                    if p.matchPage(path, exact):
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
            raise countershape.ApplicationError(s)
    
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
                p = "/" + "/".join(path[:l-i])
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
                raise countershape.ApplicationError(e%(page.path))
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
            raise countershape.ApplicationError(s)
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
        for d in page():
            yield d
        self.post(page)


class Application(BaseApplication):
    logErr = sys.stderr
