"""
    grok.py

    A module for extracting simple information from Python source, without
    interpreting the file.
"""

# FIXME: This module should be extracted from Countershape, with all the
# document generation functionality removed. It would benefit from being a
# free-standing, simple pseudo-parser.

# FIXME: Make flags more sophisticated. Warnings for unknown flags, conflicting
# flags. Also implies that we need a warnings framework.

import tokenize, itertools, os.path
import utils, html, textish, template

CSS_CLASS = "grokdoc"

_whitespace = set([ "NL", "INDENT", "NEWLINE", "DEDENT"])
_whitespaceAndComments = _whitespace.copy()
_whitespaceAndComments.add("COMMENT")


class _TokenIter:
    def __init__(self, tokgen):
        self._gen = tokgen
        self._pushBuf = []
        self._done = False

    def push(self, lst):
        self._pushBuf.extend(lst)

    def next(self):
        if self._pushBuf:
            return self._pushBuf.pop()
        else:
            if self._done:
                return ("DEDENT", "")
            else:
                n = self._gen.next()
                if utils.isStringLike(n[0]):
                    name = n[0]
                else:
                    name = tokenize.tok_name[n[0]]
                if name == "ENDMARKER":
                    self._done = True
                    return ("DEDENT", "")
                else:
                    return (name, n[1])

    def __iter__(self):
        return self
        

class _TokProc:
    """
        Simple token processor class.
    """
    _cubictemp_unescaped = True
    def _syntax(self, s):
        syntax = template.pySyntax.withConf(
                    cssClass = "grokdoc",
                )
        return html.RawStr(syntax(s))

    def _forward(self, toks, s):
        """
            Eat and discard until a token in s is found.
        """
        acc = []
        while 1:
            i = toks.next()
            if i[0] in s:
                return acc
            else:
                acc.append(i)

    def _eatBlock(self, toks):
        """
            Eat tokens until the next block is consumed. Should be called from
            a line _before_ the block to be consumed.
        """
        indent = 0
        acc, comment = [], []
        while 1:
            n = toks.next()
            acc.append(n)
            if n[0] == "INDENT":
                indent += 1
            elif n[0] == "DEDENT":
                indent -= 1
                if indent < 0:
                    toks.push(reversed(comment))
                    return acc
            if n[0] == "COMMENT":
                comment.append(n)
            elif n[0] != "DEDENT":
                comment = []

    def _getArgs(self, toks):
        """
            Retrieves an argument block. The current token should be the
            opening bracket of the argument block.

            Returns a a list of key, value argument pairs.
        """
        toks.next()
        indent = 0
        lst = []
        currName, currValue = [], []
        name = True
        for i in toks:
            if i[0] == "OP" and i[1] == ")":
                indent -= 1
                if indent < 0:
                    break
            elif i[0] == "OP" and i[1] == "(":
                indent += 1
            if indent == 0:
                if i[0] == "OP" and i[1] == ",":
                    lst.append((currName, currValue))
                    currName, currValue = [], []
                    name = True
                else:
                    if name:
                        if i[0] == "OP" and i[1] == "=":
                            name = False
                        else:
                            currName.append(i[1])
                    else:
                        currValue.append(i[1])
            else:
                currValue.append(i[1])
                # Make the spacing of nested lists nice
                if i[0] == "OP" and i[1] == ",":
                    currValue.append(" ")
        if currName:
            lst.append((currName, currValue))
        nl = []
        for i in lst:
            nl.append(("".join(i[0]), "".join(i[1])))
        return nl

    def _findStr(self, toks):
        """
            Finds the next string, ignoring whitespace. Returns an empty string
            if no following string is found.

            This method (and a number of others) are complicated because the
            Python tokenizer does not recognize the indentation of comments.
            This means that an indented comment at the beginning of the block
            will PRECEDE the indent token which will be generated for the first
            non-whitespace element of the block. The same is true for comments
            following a dedent.
        """
        ret, flags = "", set([])
        pushback = []
        while 1:
            try:
                i = toks.next()
            except StopIteration:
                break
            nodoc = True
            if i[0] == "DEDENT":
                break
            elif i[0] == "COMMENT" and i[1].startswith("#grok:"):
                flags.update(set(i[1][6:].strip().split(",")))
            elif nodoc and i[0] == "STRING":
                # FIXME: Use .decode here instead?
                ret = eval(i[1])
                pushback = []
                nodoc = False
            elif i[0] in _whitespaceAndComments:
                pushback.append(i)
            else:
                pushback.append(i)
                break
        x = 0
        # Remove indents
        pushback = [i for i in pushback if i[0] != "INDENT"]
        # Skip whitespace
        for x, e in enumerate(pushback):
            if e[0] not in _whitespace:
                break 
        toks.push(reversed(pushback[x:]))
        return ret, flags

    def _getNamespace(self, tokitr):
        acc = []
        doc, flags = self._findStr(tokitr)
        indent = 0
        namespace = utils.OrderedSet()
        comment = []
        while 1:
            i = tokitr.next()
            if i == ('NAME', 'def'):
                f = Func(tokitr)
                namespace.append(f)
            elif i == ('NAME', 'class'):
                k = Klass(tokitr)
                namespace.append(k)
            elif i[0] == "INDENT":
                indent += 1
            elif i[0] == "DEDENT":
                indent -= 1
                if indent < 0:
                    tokitr.push([("COMMENT", x) for x in reversed(comment)])
                    return doc, flags, namespace
            elif i[0] == 'NAME':
                n = tokitr.next()
                if n == ('OP', '='):
                    namespace.append(Variable(i[1], comment, tokitr))
                else:
                    tokitr.push([n])

            if i[0] == "COMMENT":
                comment.append(i[1])
            elif not i[0] == "DEDENT":
                comment = []

    def __hash__(self):
        return hash(self.name)


class Variable(_TokProc):
    name = None
    doc = ""
    value = None
    def __init__(self, name, comment, tok):
        self.name = name
        if comment:
            self.doc = " ".join([i.lstrip("#") for i in comment])
        else:
            doc = ""
        val = []
        for i in self._forward(tok, "NEWLINE"):
            if not i[0] == "NL":
                val.append(i[1])
                if i[1] == ",":
                    val.append(" ")
        self.value = "".join(val)

    def __str__(self):
        s = html.TR(
            html.TD(
                self._syntax(self.name + " = " + self.value)
            ),
            html.TD(textish.Textish(self.doc)),
        )
        return unicode(s)


class Func(_TokProc):
    name = None
    doc = ""
    arguments = None
    # FIXME: Make this class, and other portions of the code dealing with
    # arguments, return data compatible with inspect.formatargspec.
    def __init__(self, tok):
        self.doc, self.arguments, self.flags = "", None, set([])
        n = tok.next()
        self.name = n[1]
        self.arguments = self._getArgs(tok)
        n = tok.next()
        assert n == ('OP', ':')
        n = tok.next()
        if n[0] == "NEWLINE":
            self.doc, self.flags = self._findStr(tok)
            self._eatBlock(tok)
        else:
            self._forward(tok, ["NEWLINE"])

    def formatArgSpec(self, arguments):
        args = []
        for i in arguments:
            if i[1]:
                args.append("%s=%s"%i)
            else:
                args.append("%s"%i[0])
        return ", ".join(args)

    def __str__(self):
        s = html.DIV(_class="grokdoc_function")
        args = self.formatArgSpec(self.arguments)
        s.addChild(
            html.DIV(
                self._syntax("def %s(%s)"%(self.name, args)),
                _class="grokdoc_function_title"
            )
        )
        if self.doc:
            s.addChild(
                html.DIV(textish.Textish(self.doc), _class="grokdoc_description")
            )
        return unicode(s)


class _NSObj(_TokProc):
    def __getitem__(self, key):
        return self.namespace[key]

    def get(self, key, default=None):
        return self.namespace.get(key, default)

    def _mkDict(self, ns):
        d = {}
        for i in ns:
            d[i.name] = i
        return d

    def functions(self, hidden=False):
        """
            Returns a list of functions. Include hidden functions if hidden is
            true.

            Functions are hidden when:
                - The function name begins with an underscore.
                - UNLESS: the function name begins and ends with double
                  underscores.
                - BUT an __init__ function with no arguments and no docstring is
                  also hidden.
        """
        for i in self.order:
            if isinstance(i, Func):
                if i.name.startswith("__") and i.name.endswith("__"):
                    special = True
                else:
                    special = False

                if hidden:
                    yield i
                elif i.name.startswith("_") and not special:
                    if "include" in i.flags:
                        yield i
                    else:
                        continue
                else:
                    if "exclude" in i.flags:
                        continue
                    yield i


    def variables(self, hidden=False):
        """
            Generator yielding Variable instances. Include hidden variables if
            hidden is true.

            Variables are hidden if the variable name begins with an
            underscore.
        """
        for i in self.order:
            if isinstance(i, Variable):
                if hidden or (not i.name.startswith("_")):
                    yield i

    def classes(self, hidden=False):
        """
            Returns a list of classes. 
        """
        for i in self.order:
            if isinstance(i, Klass):
                if i.name.startswith("_"):
                    if "include" in i.flags:
                        yield i
                else:
                    if not "exclude" in i.flags:
                        yield i


class Klass(_NSObj):
    name = None
    doc = ""
    arguments = None
    flags = None
    def __init__(self, tok):
        self.doc, self.arguments, self.order = None, [], []
        self.flags = set([])
        n = tok.next()
        self.name = n[1]
        n = tok.next()
        if n == ('OP', '('):
            tok.push([n])
            self.arguments = self._getArgs(tok)
            n = tok.next()
        assert n == ('OP', ':')
        n = tok.next()
        if n[0] == "NEWLINE":
            self.doc, self.flags, self.order = self._getNamespace(tok)
        else:
            self._forward(tok, ["NEWLINE"])
        self.namespace = self._mkDict(self.order)

    def signature(self):
        it = self.get("__init__")
        if it:
            args = [i for i in it.arguments if i[0] != "self"]
            return "%s(%s)"%(self.name, it.formatArgSpec(args))
        else:
            return "%s()"%self.name

    def signatureDoc(self):
        s = html.DIV(_class="grokdoc_class")
        s.addChild(
                html.DIV(
                    self._syntax(self.signature()),
                    _class="grokdoc_class_title"
                )
            )
        it = self.get("__init__")
        if it and it.doc:
            s.addChild(
                html.DIV(textish.Textish(it.doc), _class="grokdoc_description")
            )
        return s

    def __str__(self):
        s = html.DIV(_class="grokdoc_class")
        args = "(" + ", ".join([i[0] for i in self.arguments]) + ")"
        s.addChild(
                html.DIV(
                    self._syntax("class " + self.name + args),
                    _class="grokdoc_class_title"
                )
            )

        description = html.DIV(_class="grokdoc_description")
        if self.doc:
            description.addChild(
                html.DIV(textish.Textish(self.doc))
            )
        variables = list(self.variables())
        if variables:
            t = html.TABLE(_class="grokdoc_vartable")
            t.addChildrenFromList([i for i in variables])
            description.addChild(t)

        functions = list(self.functions())
        if functions:
            description.addChildrenFromList(
                    [i for i in functions]
            )

        s.addChild(description)
        return unicode(s)


class Module(_NSObj):
    name = None
    doc = ""
    flags = None
    def __init__(self, fname, name):
        self.fname, self.name = fname, name
        f = open(fname)
        gen = tokenize.generate_tokens(f.readline)
        self.doc, self.flags, order = self._getNamespace(
            _TokenIter(gen)
        )
        self.order = order
        self.namespace = self._mkDict(order)

    def __str__(self):
        s = html.DIV(_class="grokdoc_module")
        if self.doc:
            s.addChild(
                html.P(textish.Textish(self.doc)),
            )
        variables = list(self.variables())
        if variables:
            t = html.TABLE(_class="grokdoc_vartable")
            t.addChildrenFromList([i for i in variables])
            s.addChild(t)

        functions = list(self.functions())
        if functions:
            s.addChildrenFromList(
                [
                    html.P(*[i for i in functions]),
                ]
            )

        classes = list(self.classes())
        if classes:
            s.addChildrenFromList(
                [
                    html.P(*[i for i in classes]),
                ]
            )
        return unicode(s)

    def __call__(self, path=None):
        if not path:
            return self
        p = path.split(".")
        cur = self
        for i in p:
            try:
                cur = cur[i]
            except KeyError:
                raise ValueError, "No such path: %s"%path
        return cur


class Project:
    def __init__(self, path):
        self.paths = {}
        for i in utils.walkTree(path):
            if i.endswith(".py"):
                modpath, n = os.path.split(i)
                if modpath:
                    modpath = modpath.split(os.path.sep)
                    modpath.append(n[:-3])
                    modpath = ".".join(modpath)
                else:
                    modpath = n[:-3]
                self.paths[modpath] = Module(os.path.join(path, i), i)

    def __call__(self, path):
        p = path.split(".")
        module, subpath = None, None
        for i in range(len(p)):
            sub = ".".join(p[:i+1])
            if sub in self.paths:
                module, subpath = self.paths[sub], p[i+1:]
        if not module:
            raise ValueError, "No such path: %s."%path
        return module(".".join(subpath))


def parse(path):
    if os.path.isdir(path):
        return Project(path)
    else:
        return Module(path, os.path.basename(path))
