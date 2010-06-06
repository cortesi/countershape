import copy
import utils
import tinytree

encoding = "utf-8"

class rawstr(unicode):
    _cubictemp_unescaped = True


class _Renderable(tinytree.Tree):
    """
        This is the basic interface for all the renderable elements in
        Countershape. Each renderable is a node in a tree of other renderables.
        You can do two things with a renderable: you can inject data into it
        through the __call__ method, or you can stringify it.

        This class also provides an .id attribute.

        When you call a renderable, a manipulable copy incorporating the
        specified data is returned.
    """
    def addChild(self, node):
        """
            Add a child to this node. If the node is not a valid tinytree node,
            we treat it as a string, and wrap it in a node object.
        """
        if not isinstance(node, tinytree.Tree):
            node = Str(node)
        tinytree.Tree.addChild(self, node)

    def __call__(self, *args, **kwargs):
        """
            The basis of the renderable interface: when called, return a
            modifiable copy of ourselves, and act on the data passed. What it
            means to act on the data is left intentionally vague - different
            node types might do different things. This default implementation
            also calls all children the supplied arguments.

            NOTE: it is very important that this call returns a copy that can
            be modified safely.
        """
        x = copy.copy(self)
        x.children = []
        for i in self.children:
            x.addChild(i(*args, **kwargs))
        return x

    def __str__(self):
        try:
            l=[unicode(i) for i in self.children]
        except UnicodeDecodeError:
            l=[unicode(str(i),'latin-1','ignore') for i in self.children]
        return "".join(l)


class RawStr(_Renderable):
    def __init__(self, s):
        _Renderable.__init__(self)
        self.s = s

    def __unicode__(self):
        return unicode(self.s)


class Str(_Renderable):
    def __init__(self, s):
        _Renderable.__init__(self)
        self.s = s

    def __unicode__(self):
        return unicode(utils.escape(self.s))
    

class _Tag(_Renderable):
    """
        Tags are dictionary-like objects, containing HTML tag attributes as
        key/value pairs.
    """
    _cubictemp_unescaped = True
    def __init__(self, _tagname, children, **kwargs):
        _Renderable.__init__(self, children)
        self.attrs = {}
        self.name = utils.escape(_tagname)
        for k, v in kwargs.items():
            self[k] = v

    def addCSSClass(self, klass):
        """
            Add a CSS class to this tag.
        """
        if self.has_key("class"):
            self["class"] = self["class"] + " " + klass
        else:
            self["class"] = klass

    def __setitem__(self, k, v):
        if k.startswith("_"):
            k = k[1:]
        k = k.lower()
        if k == "id":
            self.id = v
        self.attrs[k.lower()] = v

    def __call__(self, valobj=None, **kwargs):
        x = _Renderable.__call__(self, valobj, **kwargs)
        x.attrs = self.attrs.copy()
        return x

    def __getitem__(self, k):
        return self.attrs[k]

    def has_key(self, k):
        return self.attrs.has_key(k)

    def _makeAttrs(self):
        tlist = []
        for k, v in self.attrs.items():
            tlist.append("%s=\"%s\""%(utils.escape(k), utils.escape(v)))
        return (" " if tlist else "") + " ".join(tlist)


class HalfTag(_Tag):
    def __init__(self, _tagname, **kwargs):
        _Tag.__init__(self, _tagname, [], **kwargs)

    def __str__(self):
        return "<%s %s/>"%(
            utils.escape(self.name),
            self._makeAttrs()
        )


class FullTag(_Tag):
    def __init__(self, _tagname, *_tagcontents, **attrs):
        _Tag.__init__(
            self,
            _tagname,
            _tagcontents,
            **attrs
        )

    def __str__(self):
        try:
            l=[unicode(i) for i in self.children]
        except UnicodeDecodeError:
            l=[unicode(str(i),'latin-1','ignore') for i in self.children]
        return "<%s%s>%s</%s>"%(
            self.name,
            self._makeAttrs(),
            "".join(l),
            self.name
        )


class _SmartTag(FullTag):
    def __init__(self, *_tagcontents, **attrs):
        FullTag.__init__(self, self._tagtype, *_tagcontents, **attrs)


class _SmartHalfTag(HalfTag):
    def __init__(self, **attrs):
        HalfTag.__init__(self, self._tagtype, **attrs)


class HTML(_SmartTag): _tagtype="html"
class BODY(_SmartTag): _tagtype="body"
class HEAD(_SmartTag): _tagtype="head"
class META(_SmartHalfTag): _tagtype="meta"
class TITLE(_SmartTag): _tagtype="title"
class DIV(_SmartTag): _tagtype="div"
class SPAN(_SmartTag): _tagtype="span"
class CODE(_SmartTag): _tagtype="code"
class PRE(_SmartTag): _tagtype="pre"
class B(_SmartTag): _tagtype="b"
class P(_SmartTag): _tagtype="p"
class H1(_SmartTag): _tagtype="h1"
class H2(_SmartTag): _tagtype="h2"
class H3(_SmartTag): _tagtype="h3"
class H4(_SmartTag): _tagtype="h4"
class H5(_SmartTag): _tagtype="h5"
class H6(_SmartTag): _tagtype="h6"
class LI(_SmartTag): _tagtype="li"
class A(_SmartTag): _tagtype="a"
class SELECT(_SmartTag): _tagtype="select"
class OPTION(_SmartTag): _tagtype="option"
class OPTGROUP(_SmartTag): _tagtype="optgroup"
class FORM(_SmartTag): _tagtype="form"
class LEGEND(_SmartTag): _tagtype="legend"
class FIELDSET(_SmartTag): _tagtype="fieldset"
class LABEL(_SmartTag): _tagtype="label"
class TEXTAREA(_SmartTag): _tagtype="textarea"
class TABLE(_SmartTag): _tagtype="table"
class COLGROUP(_SmartTag): _tagtype="colgroup"
class COL(_SmartTag): _tagtype="col"
class TD(_SmartTag): _tagtype="td"
class TH(_SmartTag): _tagtype="th"
class TR(_SmartTag): _tagtype="tr"
class TBODY(_SmartTag): _tagtype="tbody"
class THEAD(_SmartTag): _tagtype="thead"
class TFOOT(_SmartTag): _tagtype="tfoot"
class EM(_SmartTag): _tagtype="em"
class DL(_SmartTag): _tagtype="dl"
class DT(_SmartTag): _tagtype="dt"
class DD(_SmartTag): _tagtype="dd"
class BUTTON(_SmartTag): _tagtype="button"
class SCRIPT(_SmartTag): _tagtype="script"
class STYLE(_SmartTag): _tagtype="style"
class CENTER(_SmartTag): _tagtype="center"
class LINK(_SmartHalfTag): _tagtype="link"
class IMG(_SmartHalfTag): _tagtype="img"
class INPUT(_SmartHalfTag): _tagtype="input"
class BR(_SmartHalfTag): _tagtype="br"
class HR(_SmartHalfTag): _tagtype="hr"


class UL(FullTag):
    _lst = "ul"
    def __init__(self, items, **attrs):
        lst = []
        for i in items:
            if isinstance(i, LI):
                lst.append(i)
            else:
                lst.append(LI(i))
        FullTag.__init__(self, self._lst, *lst, **attrs)


class OL(UL):
    _lst = "ol"


class Group(_Renderable):
    _cubictemp_unescaped = True
    def __init__(self, *children):
        c = []
        for i in children:
            if isinstance(i, tinytree.Tree):
                c.append(i)
            else:
                c.append(Str(i))
        _Renderable.__init__(self, c)


class Value(_Renderable):
    """
        A simple renderable that pulls a value from the call namespace, and
        inserts it verbatim.
    """
    def __init__(self, name):
        """
                name   -  The field name (i.e. key or attribute) to act upon.
        """
        _Renderable.__init__(self)
        self.name = name
        self.value = ""

    def __call__(self, valobj=None, **kwargs):
        x = _Renderable.__call__(self, valobj, **kwargs)
        x.value = kwargs.get(self.name) or ""
        return x

    def __str__(self):
        return unicode(self.value)


