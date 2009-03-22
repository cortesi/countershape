import cubictemp, tinytree
import model, state, html, widgets, textish

try:
    import pygments, pygments.lexers, pygments.formatters
    from pygments import highlight
    class Syntax:
        def __init__(self,
                     lexer,
                     style="native",
                     linenostep=0,
                     linenos=False,
                     cssClass="highlight"):
            self.lexer, self.style = lexer, style
            self.linenostep, self.linenos = linenostep, linenos
            self.cssClass = cssClass

        def withConf(self,
                     style="native",
                     linenostep=0,
                     linenos=False,
                     cssClass="highlight"):
            return Syntax(lexer=self.lexer,
                          style=style,
                          linenostep=linenostep,
                          linenos=linenos,
                          cssClass=cssClass)

        def __call__(self, txt):
            txt = txt.rstrip()
            fargs = dict(style=self.style)
            if self.linenos:
                fargs["linenos"] = self.linenos
            if self.linenostep:
                fargs["linenostep"] = self.linenostep
            if self.cssClass:
                fargs["cssclass"] = self.cssClass
            return "%s\n"%unicode(
                    pygments.highlight(
                        txt,
                        self.lexer,
                        pygments.formatters.HtmlFormatter(**fargs)
                    )
                )
    pySyntax            = Syntax(pygments.lexers.PythonLexer())
    pyTracebackSyntax   = Syntax(pygments.lexers.PythonTracebackLexer())
    cssSyntax           = Syntax(pygments.lexers.CssLexer())
    htmlSyntax          = Syntax(pygments.lexers.HtmlLexer())
    jsSyntax            = Syntax(pygments.lexers.JavascriptLexer())
except ImportError:
    class Syntax:
        def __init__(self, *args, **kwargs):
            pass

        def withConf(self, *args, **kwargs):
            return Syntax()

        def __call__(self, txt):
            return "%s\n"%unicode(txt)
    pySyntax            = Syntax(pygments.lexers.PythonLexer())
    pyTracebackSyntax   = Syntax(pygments.lexers.PythonTracebackLexer())
    cssSyntax           = Syntax(pygments.lexers.CssLexer())
    htmlSyntax          = Syntax(pygments.lexers.HtmlLexer())
    jsSyntax            = Syntax(pygments.lexers.JavascriptLexer())
    

def cubescript(txt):
    txt = txt.replace("@_!", "@!")
    txt = txt.replace("$_!", "$!")
    txt = txt.replace("_end)-->", "end)-->")
    txt = txt.replace("<!--(_for", "<!--(for")
    txt = txt.replace("<!--(_block", "<!--(block")
    return txt


def _ns():
    return dict(
        linkTo              = model.LinkTo,
        aLink               = model.ALink,
        urlTo               = model.UrlTo,
        top                 = model.Top(),
        siblingIndex        = widgets.SiblingPageIndex(),
        parentIndex         = widgets.ParentPageIndex(),
        extendedParentIndex = widgets.ExtendedParentPageIndex(),
        siblingNavBar       = widgets.SiblingNavBar,
        next                = state.page.findForwards(lambda x: x.title),
        previous            = state.page.findBackwards(lambda x: x.title),
        this                = state.page,
        # Processors
        htmlescape          = cubictemp.escape
    )


class _TemplateMixin:
    def __str__(self):
        kwargs = {}
        kwargs.update(_ns())
        kwargs.update(self._getNS())
        kwargs.update(self.nsDict)
        s = self.block(**kwargs)
        return unicode(textish.Textish(s)) if self.textish else s

    def __call__(self, *args, **kwargs):
        kwargs.update(_ns())
        kwargs.update(self._getNS())
        return cubictemp.Template.__call__(self, **kwargs)

    def _getNS(self):
        return {}


class Template(_TemplateMixin, cubictemp.Template, tinytree.Tree):
    def __init__(self, textish, *args, **kwargs):
        cubictemp.Template.__init__(self, *args, **kwargs)
        tinytree.Tree.__init__(self)
        self.textish = textish


class File(_TemplateMixin, cubictemp.File, tinytree.Tree):
    def __init__(self, textish, *args, **kwargs):
        cubictemp.File.__init__(self, *args, **kwargs)
        tinytree.Tree.__init__(self)
        self.textish = textish
