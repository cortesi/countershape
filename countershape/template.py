import cubictemp, tinytree
import model, state, html, widgets


class DummySyntax:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, txt):
        return "<pre>%s\n</pre>"%unicode(cubictemp.escape(txt))


try:
    import pygments, pygments.lexers, pygments.formatters
    from pygments import highlight
    class Syntax:
        def __init__(self, lexer, style="native", linenostep=0, linenos=False, cssClass="highlight"):
            self.style = style
            self.lexer = pygments.lexers.get_lexer_by_name(lexer)
            self.linenostep, self.linenos = linenostep, linenos
            self.cssClass = cssClass

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
except ImportError:
    Syntax = DummySyntax


def cubescript(txt):
    txt = txt.replace("@_!", "@!")
    txt = txt.replace("$_!", "$!")
    txt = txt.replace("_end)-->", "end)-->")
    txt = txt.replace("<!--(_for", "<!--(for")
    txt = txt.replace("<!--(_block", "<!--(block")
    return txt


def _ns():
    return dict(
        state               = state,
        linkTo              = model.LinkTo,
        aLink               = model.ALink,
        urlTo               = model.UrlTo,
        getPage             = state.application.getPage,
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
    def __unicode__(self):
        kwargs = {}
        kwargs.update(_ns())
        kwargs.update(self._getNS())
        kwargs.update(self.nsDict)
        s = self.block.render(**kwargs)
        value = ""
        try:
            value = unicode(self.markup(s)) if self.markup else unicode(s)
        except TypeError:
            print "Error: Check that you have a valid this.markup=markup.Markdown() or similar configuration"
            raise
        return value

    def __call__(self, *args, **kwargs):
        kwargs.update(_ns())
        kwargs.update(self._getNS())
        return cubictemp.Template.__call__(self, **kwargs)

    def _getNS(self):
        if state.page and hasattr(state.page, "namespace"):
            return state.page.namespace
        else:
            return {}


class Template(_TemplateMixin, cubictemp.Template, tinytree.Tree):
    def __init__(self, markup, *args, **kwargs):
        cubictemp.Template.__init__(self, *args, **kwargs)
        tinytree.Tree.__init__(self)
        self.markup = markup


class File(_TemplateMixin, cubictemp.File, tinytree.Tree):
    def __init__(self, markup, *args, **kwargs):
        cubictemp.File.__init__(self, *args, **kwargs)
        tinytree.Tree.__init__(self)
        self.markup = markup
