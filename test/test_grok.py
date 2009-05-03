import tokenize
import libpry
import countershape.grok

class u_TokenIter(libpry.AutoTree):
    def test_iter(self):
        gen = tokenize.generate_tokens(open("grok/one.py").readline)
        f = countershape.grok._TokenIter(gen)
        pre = f.next()
        assert len(pre) == 2
        f.push([pre])
        f.push([("ONE", "TWO")])
        n = f.next()
        assert n == ("ONE", "TWO")
        n = f.next()
        n = pre

    def test_termination(self):
        gen = tokenize.generate_tokens(open("grok/empty.py").readline)
        f = countershape.grok._TokenIter(gen)
        n = f.next()
        assert n == ("DEDENT", "")
        n = f.next()
        assert n == ("DEDENT", "")


class u_TokProc(libpry.AutoTree):
    def setUp(self):
        self.t = countershape.grok._TokProc()

    def test_forward(self):
        toks = [
            ('STRING', '"""foo"""'),
            ('STRING', '"""foo"""'),
            ('NEWLINE', '\n'),
            ('STRING', '"""foo"""'),
        ]
        i = iter(toks)
        self.t._forward(i, ["NEWLINE"])
        assert len(list(i)) == 1

    def test_findStr_empty(self):
        toks = [
            ('NEWLINE', '\n'),
            ('INDENT', '    '),
            ('NAME', 'x'),
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        self.t._findStr(itr)
        val = list(itr)
        assert len(val) == 1

    def test_findStr(self):
        toks = [
            ('NEWLINE', '\n'),
            ('STRING', '"""foo"""'),
            ('NEWLINE', '\n'),
            ('COMMENT', "#grok:include"),
            ('NEWLINE', '\n'),
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert spec == set(["include"])
        lst = list(itr)
        assert len(lst) == 1

        toks = [
            ('NEWLINE', '\n'),
            ('COMMENT', '#grok:include'),
            ('COMMENT', "#grok:exclude"),
            ('NEWLINE', '\n')
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert "include" in spec
        assert "exclude" in spec
        assert val == ''

        toks = [
            ('STRING', '"""foo"""'),
            ('NEWLINE', '\n')
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert val == 'foo'
        assert len(list(itr)) == 1

        toks = [
            ('NEWLINE', '\n'),
            ('NEWLINE', '\n'),
            ('COMMENT', '#grok:include'),
            ('NEWLINE', '\n'),
            ('NEWLINE', '\n'),
            ('STRING', '"foo"'),
            ('NEWLINE', '\n')
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert "include" in spec
        assert val == 'foo'
        assert len(list(itr)) == 1

    def test_findStr_neg(self):
        toks = [
            ('NEWLINE', '\n'),
            ('NAME', 'class'),
            ('NEWLINE', '\n')
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert val == "" 
        l = list(itr)
        assert len(l) == 2

    def test_findStr_comment(self):
        toks = [
            ('NEWLINE', '\n'),
            ('COMMENT', '# moo'),
            ('NEWLINE', '\n'),
            ('STRING', '"foo"'),
            ('NEWLINE', '\n')
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert val == "foo" 
        assert len(list(itr)) == 1

    def test_findStr_postcomment(self):
        toks = [
            ('NEWLINE', '\n'),
            ('STRING', '"foo"'),
            ('NEWLINE', '\n'),
            ('COMMENT', '# moo'),
            ('NEWLINE', '\n'),
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        val, spec = self.t._findStr(itr)
        assert val == "foo" 
        l = list(itr)
        assert len(l) == 2

    def test_getArgs(self):
        toks = [
            ('OP', '('),
            ('NAME', 'self'),
            ('OP', ')')
        ]
        val = self.t._getArgs(iter(toks))
        assert val == [("self", "")]

    def test_getArgs_complex(self):
        toks = [
            ('OP', '('),
            ('NAME', 'self'),
            ('OP', ','),
            ('NAME', 'one'),
            ('OP', ','),
            ('NAME', 'two'),
            ('OP', '='),
            ('NAME', 'func'),
            ('OP', '('),
            ('OP', '('),
            ('STRING', '"one)"'),
            ('OP', ','),
            ('STRING', '"two"'),
            ('OP', ')'),
            ('OP', ')'),
            ('OP', ','),
            ('OP', '*'),
            ('NAME', 'args'),
            ('OP', ','),
            ('OP', '**'),
            ('NAME', 'kwargs'),
            ('OP', ')'),
            ('OP', ':'),
        ]
        val = self.t._getArgs(iter(toks))
        expected = [
            ('self', ''),
            ('one', ''),
            ('two', 'func(("one)", "two"))'),
            ('*args', ''),
            ('**kwargs', '')
        ]
        assert val == expected

    def test_getArgs_empty(self):
        toks = [
            ('OP', '('),
            ('OP', ')')
        ]
        val = self.t._getArgs(iter(toks))
        assert val == []

    def test_eatBlock(self):
        toks = [
            ('NAME', 'foo'),
            ('INDENT', ''),
            ('INDENT', ''),
            ('DEDENT', ''),
            ('DEDENT', ''),
            ('DEDENT', ''),
            ('NAME', 'bar'),
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        self.t._eatBlock(itr)
        assert len(list(itr)) == 1

    def ttest_dump(self):
        f = open("grok/one.py")
        for i in tokenize.generate_tokens(f.readline):
            name = tokenize.tok_name[i[0]]
            print (name, i[1])


class uModule(libpry.AutoTree):
    def setUp(self):
        self.mod = countershape.grok.Module("grok/one.py", "one.py")

    def test_klass_signature(self):
        assert self.mod["Foo"].signature() == "Foo(one, two=\"two\")"
        assert self.mod["Short"].signature() == "Short()"

        assert self.mod["Foo"].signatureDoc()
        assert self.mod["Short"].signatureDoc()

    def test_tokenize(self):
        f = countershape.grok.parse("grok/one.py")
        assert "docstring" in f.doc
        assert f["nested"]
        assert f["global_variable"].value == "(func(func(10))+10, 12)"
        assert "comment" in f["global_variable"].doc
        assert f["global_variable2"].value == "(func(func(10))+10, 12)"
        assert f["_hidden_variable"].value == "10"

        assert len(f.namespace) == 14

        assert "docstring" in f["func"].doc

        assert f.namespace.has_key("Parent")

        assert "docstring" in f["Foo"].doc

        assert len(f["Foo"]["meth"].arguments) == 5

        assert len(f["Foo"]["meth2"].arguments) == 1
        assert not f["Foo"]["meth2"].doc

    def test_noargs(self):
        f = countershape.grok.parse("grok/one.py")
        assert not f["NoClassDoc"].namespace.keys() == ("__str__")

    def test_reprs(self):
        repr(self.mod["nested"])
        repr(self.mod["Foo"])
        repr(self.mod["global_variable"])

    def test_empty(self):
        countershape.grok.Module("grok/empty.py", "empty.py")

    def test_variables(self):
        assert len(list(self.mod.variables())) == 3
        assert len(list(self.mod.variables(True))) == 4

    def test_variables_str(self):
        assert str(list(self.mod.variables())[0])

    def test_classes(self):
        assert len(list(self.mod.classes())) == 6

    def test_doc(self):
        assert self.mod["global_variable"].doc == ' Multiline\n  comment\n'
        assert self.mod["variable"].doc == ' variabledoc\n  multiline\n'
        assert "classvardoc" in self.mod["Foo"]["classvar"].doc
        assert self.mod["Foo"]["classvar"].doc == ' classvardoc\n  multiline\n'

    def test_class_str(self):
        assert str(list(self.mod.classes())[2])
        assert str(self.mod())

    def test_functions(self):
        f = self.mod["Foo"]
        assert len(list(f.functions())) == 5
        assert len(list(f.functions(True))) == 7

    def test_flags(self):
        f = countershape.grok.parse("grok/one.py")
        assert "include" in f["func"].flags
        assert "include" in f["Foo"].flags
        
        assert "include" in self.mod.flags



class uFunc(libpry.AutoTree):
    def test_init(self):
        toks =[
            ('NAME', 'meth'),
            ('OP', '('),
            ('NAME', 'self'),
            ('OP', ')'),
            ('OP', ':'),
            ('NEWLINE', '\n'),
            ('INDENT', '        '),
            ('STRING', '"""docstr"""'),
            ('NEWLINE', '\n'),
            ('NAME', 'pass'),
            ('NEWLINE', '\n'),
            ('NL', '\n'),
            ('NL', '\n'),
            ('NL', '\n'),
            ('NL', '\n'),
            ('DEDENT', ''),
            ('NAME', 'foo'),
            ('DEDENT', ''),
        ]
        itr = countershape.grok._TokenIter(iter(toks))
        x = countershape.grok.Func(itr)
        assert x.name == "meth"
        assert x.arguments == [("self", "")]
        assert "docstr" in x.doc

    def test_short(self):
        toks = [
            ('NAME', 'meth2'),
            ('OP', '('),
            ('NAME', 'self'),
            ('OP', ')'),
            ('OP', ':'),
            ('NAME', 'pass'),
            ('NEWLINE', '\n'),
            ('NL', '\n'),
        ]
        x = countershape.grok.Func(iter(toks))
        assert x.name == "meth2"
        assert x.arguments == [("self", "")]

    def test_str(self):
        toks = [
            ('NAME', 'meth2'),
            ('OP', '('),
            ('NAME', 'self'),
            ('OP', ')'),
            ('OP', ':'),
            ('NAME', 'pass'),
            ('NEWLINE', '\n'),
            ('NL', '\n'),
        ]
        x = countershape.grok.Func(iter(toks))
        str(x)


class uProjectCShape(libpry.AutoTree):
    def setUpAll(self):
        self.p = countershape.grok.parse("../countershape")

    def test_call(self):
        self.p("model.BaseApplication.testing")

    def test_strmodule(self):
        str(self.p("model"))
        str(self.p("state"))

    def test_call_nonexistent(self):
        libpry.raises("no such path", self.p, "foo.bar.boing")
        libpry.raises("no such path", self.p, "model.bar.boing")

    def test_paths(self):
        assert self.p("model")


class uProject(libpry.AutoTree):
    def setUpAll(self):
        self.p = countershape.grok.parse("testmod")

    def test_paths(self):
        assert self.p("foo")



tests = [
    u_TokenIter(),
    u_TokProc(),
    uModule(),
    uFunc(),
    uProject(),
    uProjectCShape()
]
