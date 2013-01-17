from __future__ import with_statement
import os, os.path, re, fnmatch, shutil, shlex, string,  codecs
import model, utils, html, state, template, widgets, markup

_ConfFile = "index.py"

class Options:
    """
        An Options object, injected into the namespace as "options".

        On the commandline, options are specified either as "name=value" pairs,
        or just as names, in which case the value is True.
    """
    def __init__(self, lst):
        self.__dict__["opts"] = {}
        for i in lst:
            parts = i.split("=", 1)
            if len(parts) == 1:
                self.__dict__["opts"][i] = True
            else:
                self.__dict__["opts"][parts[0]] = parts[1]

    def __getattr__(self, attr):
        if "opts" in self.__dict__:
            if attr in self.__dict__["opts"]:
                return self.__dict__["opts"][attr]
        return False

    def __setattr__(self, attr, value):
        self.__dict__["opts"][attr] = value

    def __str__(self):
        r = []
        for k, v in self.__dict__["opts"].items():
            r.append("%s=%s"%(k, v))
        return "\n".join(r)


class _Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def getDict(self):
        return self.__dict__


def readFrom(path):
    f = open(path)
    return f.read()


class _DocMixin:
    def _getNamespace(self):
        d = {}
        for i in reversed(list(self.attrsToRoot("namespace"))):
            d.update(i)
        d["this"] = self
        if self.namespace:
            d.update(self.namespace)
        self.namespace = d

    def _nameSrc(self, name, src):
        if src:
            return name, os.path.abspath(src)
        else:
            return os.path.basename(name), os.path.abspath(name)


class _DocHTMLPage(model.HTMLPage, _DocMixin):
    link = model.Link([])
    _verbatimComponents = "pageTitle"
    _pageTitle = None
    def __init__(self, name, title, namespace=None, src=None, pageTitle=None):
        model.HTMLPage.__init__(self)
        self.name, self.src = self._nameSrc(name, src)
        self.title = title
        if not namespace:
            self.namespace = {}
        else:
            self.namespace = namespace
        self._pageTitle = pageTitle

    def pageTitle(self, *args, **kwargs):
        t = self._pageTitle or model.HTMLPage.pageTitle(self)
        prefix = self.findAttr("titlePrefix")
        if prefix:
            return "%s%s"%(prefix, t)
        else:
            return t

    def _prime(self, app):
        model.HTMLPage._prime(self, app)
        self._getNamespace()

    def _getLayoutComponent(self, attr):
        if attr in self.namespace:
            r = self.namespace[attr]
        else:
            r = model.HTMLPage._getLayoutComponent(self, attr)
        base = None
        if self.src:
            base = os.path.dirname(self.src)
        with utils.InDir(base or "."):
            if utils.isStringLike(r) and (attr not in self._verbatimComponents):
                return template.Template(self.findAttr("markup"), unicode(r))
            else:
                return r


class Page(_DocHTMLPage):
    """
        Pages are always guaranteed to have a Directory object parent.
    """
    def __init__(self, name, title=None, namespace=None, src=None, pageTitle=None):
        htmlextensions=['html','htm']
        htmlext=os.path.extsep+'html'
        filename_ext=os.path.splitext(name)
        self.fileext=None
        if len(filename_ext[1])==0 or (len(filename_ext[1])>0 and (filename_ext[1][1:]).lower() not in htmlextensions):
            self.fileext=filename_ext[1]
            name = "%s%s"%(filename_ext[0],htmlext)
        _DocHTMLPage.__init__(self, name, title, namespace, src, pageTitle)

    def _prime(self, app):
        _DocHTMLPage._prime(self, app)
        dt = self.findAttr("contentName")
        if not dt in self.namespace:
            if self.fileext is not None:
                filepath = os.path.splitext(os.path.join(self.src))[0]+self.fileext
            else:
                filepath = self.src

            try:
                s = codecs.open(os.path.join(filepath), "r", "utf-8").read()
            except UnicodeDecodeError:
                s = codecs.open(os.path.join(filepath), "r", "latin-1").read()

            if self.fileext is not None and self.fileext.lower() in [".md", ".markdown", ".mdtext"]:
                    self.namespace[dt] = template.Template(markup.Markdown(), s)
            elif self.fileext is not None and (self.fileext).lower() in [".rst", ".rest", ".rstext"]:
                    self.namespace[dt] = template.Template(markup.RST(), s)
            else:
                self.namespace[dt] = template.Template(self.findAttr("markup"), s)
            self.namespace[dt].name = self.src

    def __repr__(self):
        return "HTMLPage(%s)"%self.name


class Copy(model.BasePage, _DocMixin):
    link = model.Link([])
    def __init__(self, name, title=None, src=None):
        self.name, self.src = self._nameSrc(name, src)
        model.BasePage.__init__(self)

    def __repr__(self):
        return "Copy(%s)"%self.name

    def render(self, *args, **kwargs):
        return file(self.src, "rb").read()


class PythonPage(_DocHTMLPage):
    pygmentsStyle = "native"
    def __init__(self, name, title=None, src=None):
        if not title:
            title = os.path.basename(name)
        _DocHTMLPage.__init__(self, name, title, None, src)
        self.src = os.path.abspath(self.src)
        name = os.path.basename(name)
        self.name = self.name + ".html"

    def body(self):
        code = file(self.src).read()
        toroot = []
        for i in self.pathToRoot():
            if isinstance(i, PythonPage):
                toroot.append(i)
            else:
                break
        toroot.reverse()
        yield html.H2("/".join(i.title for i in toroot))
        yield html.rawstr(self.namespace["syntax"]("py")(code))

    def __repr__(self):
        return "PythonPage(%s)"%self.src


class PythonModule(_DocHTMLPage):
    structural = True
    def __init__(self, name, title=None, src=None):
        _DocHTMLPage.__init__(self, name, title, None, src)
        self.src = os.path.abspath(self.src)
        self.d = StaticDirectory(self.name)
        self.name = self.name + "_index.html"
        for f in sorted(os.listdir(self.src)):
            ctitle = os.path.basename(f)
            p = os.path.join(self.src, f)
            if os.path.isfile(p) and p.endswith(".py"):
                self.d.addChild(PythonPage(p))
            else:
                if os.path.exists(os.path.join(p, "__init__.py")):
                    self.d.addChild(PythonModule(p, title=f))

    def register(self, parent):
        _DocHTMLPage.register(self, parent)
        self.parent.children.insert(self.index() + 1, self.d)
        self.d.register(parent)

    def body(self):
        yield widgets.ParentPageIndex(self.getNext(), divclass="sourceindex")

    def __repr__(self):
        return "PythonModule(%s)"%self.src


class StaticDirectory(model.BasePage):
    structural = True
    internal = True
    def __init__(self, name):
        model.BasePage.__init__(self)
        self.name = name

    def __repr__(self):
        return "StaticDirectory(%s)"%self.name


class Directory(StaticDirectory, _DocMixin):
    """
        A directory that auto-constructs its contents.
    """
    internal = True
    excludePatterns = utils.fileExcludePatterns + ["*/%s"%_ConfFile, "*/_*"]
    def __init__(self, name, src=None, namespace=None):
        self.stdHeaders = []
        name, self.src = self._nameSrc(name, src)
        StaticDirectory.__init__(self, name)
        if not namespace:
            self.namespace = {}
        else:
            self.namespace = namespace

    def _prime(self, app):
        StaticDirectory._prime(self, app)
        self._getNamespace()
        self.load()

    def load(self):
        seen = set()
        fname = os.path.join(self.src, _ConfFile)
        if os.path.isfile(fname):
            ns = _Bunch(**self.namespace)
            loc = glob = dict(ns=ns, this=self, readFrom=readFrom)
            pwd = os.getcwd()
            with utils.InDir(self.src):
                execfile(_ConfFile, glob, loc)
            for c in loc["pages"]:
                if c.src:
                    seen.add(c.src)
                self.addChild(c)
            self.namespace.update(ns.getDict())

        # Copy files not explicitly listed
        for f in sorted(os.listdir(self.src)):
            fullSrc = os.path.join(self.src, f)
            for patt in self.excludePatterns:
                if fnmatch.fnmatch(fullSrc, patt):
                    break
            else:
                if not fullSrc in seen:
                    self.addChild(self.defaultAction(fullSrc))

    def defaultAction(self, src):
        """
            Default action to take for pages not in the index, and not
            explicitly excluded by excludePatterns.
        """
        if os.path.isfile(src):
            if src.endswith(".css") or src.endswith(".js"):
                urlpath = src[len(self.application.root.src):]
                self.stdHeaders.append(
                    model.UrlTo(urlpath)
                )
            return Copy(src)
        else:
            return Directory(os.path.basename(src), src)

    def __repr__(self):
        return "Directory(%s)"%self.name


class DocRoot(Directory):
    """
        The top node in the document tree.
    """
    root = True
    structural = False
    # Default namespace tag for file content
    contentName = "body"
    markup = markup.Default()
    _baseNS = dict(
        syntax              = template.Syntax,
        readFrom            = readFrom,
        cubescript          = template.cubescript,
    )
    def __init__(self, src, options=[]):
        """
            src:    Path to the top of the document tree.
            options: A list of name=value flags, with values optional.
        """
        namespace = self._baseNS.copy()
        namespace["options"] = Options(options)
        Directory.__init__(self, src, namespace=namespace)

    def __repr__(self):
        return "DocRoot(%s)"%self.name


class Doc(model.BaseApplication):
    """
        Document rendering application.
    """
    def __init__(self, root, options=[]):
        if utils.isStringLike(root):
            d = DocRoot(root, options)
        else:
            d = root
        model.BaseApplication.__init__(self, d)

    def render(self, destination):
        if not os.path.exists(destination):
            os.mkdir(destination)
        for i in self.root.preOrder():
            path = [j.name for j in i.structuralPath()]
            if (not i.internal) and (not i is self.root):
                if len(path) > 1:
                    newdir = os.path.join(destination, *path[:-1])
                    if not os.path.exists(newdir):
                        os.makedirs(newdir)
                out = self(i)
                f = open(os.path.join(destination, *path), "wb")
                if isinstance(out, unicode):
                    out = out.encode("utf-8")
                f.write(out)

    def __call__(self, page):
        return model.BaseApplication.__call__(self, page)

