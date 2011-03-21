import tinytree
import html, state, model, utils

class NavBar(html._Renderable):
    _cubictemp_unescaped = 1
    def __init__(self, items, **attrs):
        html._Renderable.__init__(self)
        self.items = items
        self.attrs = attrs

    def __call__(self, valobj=None, **kwargs):
        x = html._Renderable.__call__(self, valobj, **kwargs)
        x.items = list(self.items)[:]
        x.attrs = self.attrs.copy()
        return x

    def __str__(self):
        lst = []
        for i in self.items:
            i = state.application.getPage(i)
            if (not i.structural) or i.internal:
                continue
            if state.page.isDocDescendantOf(i):
                a = html.LI(
                    html.A(i.title, href=model.UrlTo(i), _class="selected"),
                    _class = "selected",
                )
            else:
                a = html.LI(
                    html.A(i.title, href=model.UrlTo(i))
                )
            lst.append(a)
        return unicode(html.UL(lst, **self.attrs))


class SiblingNavBar(NavBar):
    def __init__(self, sibling, **attrs):
        self.sibling = state.application.getPage(sibling)
        NavBar.__init__(self, self.sibling.siblings(), **attrs)


class _PageIndex(html._Renderable):
    _cubictemp_unescaped = True
    activeClass = "active"
    inactiveClass = "inactive"

    def __init__(self, nodespec=None, depth=None, divclass="pageindex",
                 exclude=(), currentActive=False):
        """
            nodespec: Subclass-dependent page node specification.
            depth: Depth to which index should be built.
            divclass: Class set on enclosing DIV.
            exclude: Sequence of pages to exclude from index.
            currentActive: Only set the active tag on the current page.
        """
        self.nodespec, self.depth = nodespec, depth
        self.divclass, self.exclude = divclass, exclude
        self.currentActive = currentActive

    def _indexPathToRoot(self, p, exclude):
        for i in p.pathToRoot():
            if i.title and not (i in exclude):
                yield i
            else:
                yield i.getPrevious()

    def _mkUL(self, n, exclude, depth):
        if not depth is None and depth <= 0:
            return
        itms = []
        if self.currentActive:
            rootpath = [state.page]
        else:
            rootpath = list(self._indexPathToRoot(state.page, exclude))
        for p in n:
            if p in exclude:
                continue
            if p.title:
                if p in rootpath:
                    klass = self.activeClass
                else:
                    klass = self.inactiveClass
                if p.internal:
                    itms.append(
                        html.LI(
                            html.A(p.title),
                            _class = klass
                        )
                    )
                else:
                    itms.append(
                        html.LI(
                            model.LinkTo(p),
                            _class = klass
                        )
                    )
            if p.children:
                if not depth is None:
                    d = self._mkUL(p.children, exclude, depth-1)
                else:
                    d = self._mkUL(p.children, exclude, None)
                if d:
                    itms.append(d)
        return html.UL(itms)

    def __call__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)

    def __str__(self):
        exclude = [state.application.getPage(i) for i in self.exclude]
        nodes = self._getNodes()
        d = html.DIV(
            self._mkUL(nodes, exclude, self.depth),
            _class=self.divclass
        )
        return unicode(d)


class ExtendedParentPageIndex(_PageIndex):
    def _getNodes(self):
        node = state.application.getPage(self.nodespec or state.page)
        nodes = node.findForwards(lambda x: x.title).siblings()
        nodes = [node] + [i for i in nodes if i.title]
        return nodes


class SiblingPageIndex(_PageIndex):
    def _getNodes(self):
        node = state.application.getPage(self.nodespec or state.page)
        return [i for i in node.siblings() if i.structural]


class ParentPageIndex(_PageIndex):
    def _getNodes(self):
        node = state.application.getPage(self.nodespec or state.page)
        return [node]


class PageIndex(_PageIndex):
    def _getNodes(self):
        return [state.application.getPage(i) for i in self.nodespec]


class PageTrail:
    """
        Provides a string of page links leading from the root page to
        the current page
    """
    _cubictemp_unescaped = 1
    def __init__(self, node):
        self.node = node

    def __str__(self):
        trail = self.node.pathToRoot()
        trailList = []
        for crumb in trail:
            if crumb.structural:
                if crumb.internal:
                    trailList.append(crumb.name)
                else:
                    trailList.append(unicode(model.LinkTo(crumb.path)))
        trailList.reverse()
        return " -> ".join(trailList)

