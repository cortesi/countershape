from __future__ import with_statement
import os, os.path, re, fnmatch, shutil, shlex, string
from optparse import OptionParser
import model, utils, html, state, template, form, widgets, encoding
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

_ConfFile = "index.py"

class Template(template.Template):
    def _getNS(self):
        return state.page.namespace


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
            return name, src
        else:
            return os.path.basename(name), name

    def _setDirectory(self, src):
        self.src = os.path.join(src, self.src)
    

class _DocHTMLPage(model.HTMLPage, _DocMixin):
    link = form.Link([])
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
        if pageTitle:
            self._pageTitle = pageTitle

    def pageTitle(self, *args, **kwargs):
        if self._pageTitle:
            t = self._pageTitle
        else:
            t = model.HTMLPage.pageTitle(self)
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
                return Template(self.findAttr("textish"), unicode(r))
            else:
                return r


class Page(_DocHTMLPage):
    """
        Pages are always guaranteed to have a Directory object parent.
    """ 
    def __init__(self, name, title=None, namespace=None, src=None, pageTitle=None):
        _DocHTMLPage.__init__(self, name, title, namespace, src, pageTitle)

    def _prime(self, app):
        _DocHTMLPage._prime(self, app)
        dt = self.findAttr("contentName")
        if not dt in self.namespace:
            s = open(os.path.join(self.src)).read()
            self.namespace[dt] = Template(self.findAttr("textish"), s)
            self.namespace[dt].name = self.src

    def __repr__(self):
        return "DocTemplate(%s)"%self.name


class Copy(model.Page, _DocMixin):
    link = form.Link([])
    def __init__(self, name, title=None, src=None):
        self.name, self.src = self._nameSrc(name, src)
        model.Page.__init__(self)

    def __repr__(self):
        return "Copy(%s)"%self.name

    def __call__(self, *args, **kwargs):
        yield encoding.binary(file(self.src, "rb").read())


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
        yield html.rawstr(self.namespace["pySyntax"](code))

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


class StaticDirectory(model.Page):
    structural = True
    internal = True
    def __init__(self, name):
        model.Page.__init__(self)
        self.name = name

    def __repr__(self):
        return "StaticDirectory(%s)"%self.name


class Directory(StaticDirectory, _DocMixin):
    """
        A directory that auto-constructs its contents.
    """
    excludePatterns = utils.fileExcludePatterns + ["*/%s"%_ConfFile, "*/_*"]
    stdHeaders = []
    def __init__(self, name, src=None, namespace=None):
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
                c._setDirectory(self.src)
                seen.add(c.src)
                self.addChild(c)
            self.namespace.update(ns.getDict())

        # Copy files not explicitly listed
        for f in os.listdir(self.src):
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
            # FIXME: we need to over-ride files with the same
            # name further up the tree
            if src.endswith(".css") or src.endswith(".js"):
                urlpath = src[len(self.application.root.src):]
                self.stdHeaders.append(
                    model.UrlTo(urlpath)
                )
            return Copy(src)
        else:
            return Directory(os.path.basename(src) ,src)

    def __repr__(self):
        return "Directory(%s)"%self.name


class _DocRoot(Directory):
    """
        The top node in the document tree.
    """
    root = True
    structural = False
    # Default namespace tag for file content
    contentName = "body"
    textish = True
    _baseNS = dict(
        pySyntax            = template.pySyntax,
        pyTracebackSyntax   = template.pyTracebackSyntax,
        cssSyntax           = template.cssSyntax,
        htmlSyntax          = template.htmlSyntax,
        jsSyntax            = template.jsSyntax,
        cubescript          = template.cubescript,
    )
    def __init__(self, src):
        """
            src:    Path to the top of the document tree.
        """
        Directory.__init__(self, src, namespace=self._baseNS.copy())

    def __repr__(self):
        return "DocRoot(%s)"%self.name


class _DocApplication(model.BaseApplication):
    """
        Document rendering application.
    """
    def __init__(self, root):
        model.BaseApplication.__init__(self, root)

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
                f = open(os.path.join(destination, *path), "w")
                f.write(out)
            d = i.__dict__.get("resources")
            if d:
                partDest = os.path.join(destination, *path)
                for local, url in d.paths.values():
                    p, f = os.path.split(url)
                    dstdir = os.path.join(partDest, p)
                    if not os.path.isdir(dstdir):
                        os.makedirs(dstdir)
                    shutil.copy(
                        local,
                        os.path.join(partDest, url)
                    )

    def __call__(self, page):
        return list(model.BaseApplication.__call__(self, page))[0]
        

# begin nocover
class CSDoc:
    usage = "usage: %prog [options] src dst"
    description = "Renders a Countershape documentation tree."
    def getParser(self):
        parser = OptionParser(self.usage, description=self.description)
        parser.add_option("-s", "--structure",
                          action="store_true", dest="structure", default=False,
                          help="Show site structure.")
        parser.add_option("-d", "--dummy",
                          action="store_true", dest="dummy", default=False,
                          help="Perform a dummy run - don't render any files.")
        return parser

    def sanity(self, parser, options, args):
        if options.structure:
            if len(args) < 1:
                parser.error("Missing source specification.")
        else:
            if len(args) != 2:
                parser.error("Please pass source and destination.")
            if os.path.abspath(args[0]) == os.path.abspath(args[1]):
                parser.error("Refusing to render documentation source onto itself.")

    def getDoc(self, path):
        d = _DocRoot(path)
        a = _DocApplication(d)
        return d, a

    def run(self, root, app, options, args):
        if options.structure:
            root.dump()
        elif not options.dummy:
            app.render(args[1])

    def main(self):
        parser = self.getParser()
        options, args = parser.parse_args()
        self.sanity(parser, options, args)
        root, app, = self.getDoc(args[0])
        self.run(root, app, options, args)
