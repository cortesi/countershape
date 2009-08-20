"""
    Textish is a lightweight markup language similar to MarkDown. It provides
    the minimum needed to produce reasonably readable text destined to become
    HTML.
"""
import HTMLParser, re
import utils
import tinytree

# TODO
#
# - Short-hand way of specifying verbatim text. This is especially
# needed for code snippets in docstrings.
# - Escaping for underscores and other syntactically significant characters.
# - Ability to declare an HTML chunk a heading, i.e.:
    #   <a href="foo">Foo</a>
    #   =====================

# The structure of this module is an experiment, and the jury is still out as
# to whether it's a success. The basic idea is that the parsing process
# proceeds through iterative transformations on a tree, beginning with a flat
# list of HTML and text blocks.

class _ExtractHTML(HTMLParser.HTMLParser):
    _splitRe = re.compile(r"(\A\s*\n\s*\n)|(\n\s*\n)+", re.MULTILINE|re.VERBOSE)
    def __init__(self, txt):
        HTMLParser.HTMLParser.__init__(self)
        self.txt = txt
        self.depth = 0
        self.current = None
        self.blockOffsets = []
        self._savepos = False

        self.feed(txt)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        if self.depth == 1:
            self.current = self.getpos()

    def handle_endtag(self, tag):
        self.depth -= 1
        if self.depth == 0:
            self._savepos = True

    # This sucks, but the Python HTML parsing libraries seem to have been
    # perversely designed to be as useless as possible. This dodgy maneuvre is
    # needed to record the position at the _end_ of the endtag, as opposed to
    # the beginning.
    def updatepos(self, i, k):
        r = HTMLParser.HTMLParser.updatepos(self, i, k)
        if self._savepos:
            self.blockOffsets.append((self.current, (self.lineno, self.offset)))
            self._savepos = False
        return r

    def _getData(self, data, fromL, fromO, toL, toO):
        """
            Retrieves a block of data as a string.

            data            - list of line strings.
            fromL, fromO    - from line and offset
            toL, toO        - to line and offset
        """
        fromL, toL = fromL-1, toL-1
        ret = []
        if fromL == toL:
            ret.append(data[fromL][fromO:toO])
        else:
            ret.append(data[fromL][fromO:])
            ret.extend(data[fromL+1:toL])
            ret.append(data[toL][0:toO])
        return "".join(ret)

    def _splitText(self, txt):
        """
            Splits txt at blank lines, and returns a sequence of _Text objects.
            The blank lines themselves are returned as part of the sequence.
        """
        ret = []
        if txt.strip():
            for i in self._splitRe.split(txt):
                if i:
                    if i.strip():
                        ret.append(_Text(i))
                    else:
                        ret.append(_Terminal())
        else:
            if txt:
                ret.append(_Text(txt))
        return ret

    def getBlocks(self):
        """
            Returns a list of strings and _HTMLBlock objects.
        """
        data = self.txt.splitlines(True)
        blocks = []
        line, off = 1, 0
        for i in self.blockOffsets:
            blocks.extend(
                self._splitText(
                    self._getData(data, line, off, i[0][0], i[0][1])
                )
            )
            line, off = i[1]
            blocks.append(
                _HTML(self._getData(data, i[0][0], i[0][1], line, off))
            )
        if data:
            blocks.extend(
                self._splitText(
                    self._getData(data, line, off, len(data), len(data[-1]))
                )
            )
        if not blocks or not isinstance(blocks[0], _Terminal):
            blocks.insert(0, _Terminal())
        return blocks


class _Terminal(tinytree.Tree):
    def __str__(self):
        return ""

    def __eq__(self, other):
        return isinstance(other, self.__class__)
    
    def __repr__(self):
        return "<Terminal>"


class _Collection(tinytree.Tree):
    def collect(self, *skip):
        skip = list(skip)
        skip.append(_Terminal)
        skip.append(self.__class__)
        n = self
        while 1:
            n = n.getNext()
            if not n or any([isinstance(n, s) for s in skip]):
                break
            elif n:
                n.remove()
                self.addChild(n)


class _Chunk(_Collection):
    _footnoteRe = re.compile(
        r"""
            \w(\[.+\])
        """,
        re.MULTILINE|re.VERBOSE|re.DOTALL
    )
    def __init__(self, s):
        tinytree.Tree.__init__(self)
        self.s = s
        self._paraSkip = [
            _Paragraph,
            _ListItem,
            _DefDef,
            _DefTerm,
            _Heading,
            _HTML
        ]

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.s == other.s)

    def _makeParagraphs(self):
        if not any([isinstance(self.parent, k) for k in self._paraSkip]):
            if not any([isinstance(self, k) for k in self._paraSkip]):
                p = self.reparent(_Paragraph())
                p.collect()

    def __repr__(self):
        s = self.s
        if len(s) > 10:
            s = s[:10] + "..."
        return "%s(%s)"%(self.__class__.__name__[1:], repr(s))

    def __str__(self):
        return self.s


class _HTML(_Chunk): pass


class _Text(_Chunk):
    _splitLiRe = re.compile(r"^\s*[\*\+\-]", re.MULTILINE)
    _isLiRe = re.compile(r"\A\s*[\*\+\-]", re.MULTILINE)
    _isDefRe = re.compile(
        r"""
            \A\s*\:(?P<keyword>\w+)
        """,
        re.MULTILINE|re.VERBOSE
    )
    _splitDefRe = re.compile(
        r"""
            ^\s*\:(?P<keyword>(\*|\w)+)
        """,
        re.MULTILINE|re.VERBOSE
    )
    _ws = "[ \t]"
    _headingRe = re.compile(
        r"""
            \s*(?P<depth>:*)
            (?P<text>[^\n]+)\n
            [ \t]*(?P<type>[=-]+)[ \t]*
        """,
        re.MULTILINE|re.VERBOSE
    )
    _markupRe = re.compile(
        r"""
            ((?:\b__\w.*?\w__\b) | (?:\b_\w.*?\w_\b))
        """,
        re.MULTILINE|re.VERBOSE|re.DOTALL
    )
    def _splitListItems(self):
        if not isinstance(self.getPrevious(), _Terminal):
            return
        if self._isLiRe.match(self.s):
            chunks = self._splitLiRe.split(self.s)
            lst = []
            for i in [x for x in chunks]:
                if i:
                    lst.append(
                        _ListItem(
                            [_Text(i)]
                        )
                    )
            self.replace(*lst)
        elif self._isDefRe.match(self.s):
            lst = []
            matches = list(self._splitDefRe.finditer(self.s))
            for i, m in enumerate(matches):
                if i < len(matches)-1:
                    txt = self.s[m.end():matches[i+1].start()].strip()
                else:
                    txt = self.s[m.end():].strip()
                lst.append(
                    _DefTerm(m.group("keyword"))
                )
                lst.append(
                    _DefDef(
                        [
                            _Text(txt)
                        ]
                    )
                )
            self.replace(*lst)

    def _makeHeadings(self, hBase):
        m = self._headingRe.match(self.s)
        if m:
            txt = m.group("text")
            if m.group("depth"):
                depth = len(m.group("depth"))
            else:
                depth = 0
            if not depth:
                if m.group("type")[0] == "=":
                    depth = 1
                else:
                    depth = 2
            h = _Heading(depth + hBase, txt)
            self.replace(h)

    def _makeMarkup(self):
        lst = []
        for i in self._markupRe.split(self.s):
            if i.startswith("__") and i.endswith("__"):
                lst.append(
                    _Strong(
                        [_Text(i[2:-2])]
                    )
                )
            elif i.startswith("_") and i.endswith("_"):
                lst.append(
                    _EM(
                        [_Text(i[1:-1])]
                    )
                )
            else:
                lst.append(_Text(i))
        self.replace(*lst)


class _Wrap(_Collection):
    def __repr__(self):
        return "<%s>"%self.__class__.__name__[1:]

    def __str__(self):
        l = [unicode(i) for i in self.children]
        return "<%s>%s</%s>"%(self.tag, "".join(l), self.tag)
                

class _Strong(_Wrap):
    tag = "strong"


class _EM(_Wrap):
    tag = "em"
    

class _Heading(_Chunk):
    def __init__(self, depth, s):
        _Chunk.__init__(self, s)
        self.depth = depth

    def __str__(self):
        return "<h%s>%s</h%s>"%(self.depth, self.s, self.depth)


class _DefDef(_Wrap):
    tag = "dd"


class _DefTerm(_Chunk):
    def __str__(self):
        return "<dt>%s</dt>"%self.s


class _DefList(_Wrap):
    # Wrap this list's children in P tags?
    tag = "dl"
    def _doWrap(self):
        for i in self.children:
            if isinstance(i, _DefDef):
                i.inject(_Paragraph())


class _ListItem(_Wrap):
    tag = "li"


class _List(_Wrap):
    # Wrap this list's children in P tags?
    tag = "ul"
    def _doWrap(self):
        for i in self.children:
            i.inject(_Paragraph())


class _Paragraph(_Wrap):
    tag = "p"


class Textish(tinytree.Tree):
    def __init__(self, s, hBase=0):
        x = _ExtractHTML(s)
        self.hBase = hBase
        tinytree.Tree.__init__(self, x.getBlocks())

        # Our parsing process is a series of transformations on the tree
        self._call("_splitListItems")
        self._collectLists()
        self._call("_makeHeadings", self.hBase)
        self._call("_makeParagraphs")
        self._call("_makeMarkup")

    def _skipChildren(self, itr, node):
        for n in itr:
            if not node.isDescendantOf(n):
                itr.push(n)
                return                

    def _collector(self, klass, *items):
        """
            Collects items of the specified types in containers of type klass.

            :klass Container class to collect items in.
            :items Classes that should be collected.
        """
        current = None
        # Make a copy - we'll be modifying the tree as we iterate
        itr = utils.BuffIter(list(self.preOrder()))
        for i in itr:
            if any([isinstance(i, x) for x in items]):
                if not current:
                    current = klass()
                    i.replace(current)
                else:
                    i.remove()
                current.addChild(i)
                i.collect(*items)
                self._skipChildren(itr, current)
            elif isinstance(i, _Terminal) and current:
                i.remove()
            else:
                if current:
                    current._doWrap()
                current = False
        
    def _collectLists(self):
        self._collector(_List, _ListItem)
        self._collector(_DefList, _DefDef, _DefTerm)

    def _call(self, meth, *args, **kwargs):
        # Make a copy - we'll be modifying the tree as we iterate
        l = [i for i in self.preOrder() if hasattr(i, meth)]
        for i in l:
            getattr(i, meth)(*args, **kwargs)

    def __str__(self):
        l = [unicode(i) for i in self.children]
        return "".join(l)

    def __repr__(self):
        return "Textish"
