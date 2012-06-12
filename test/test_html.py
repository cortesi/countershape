import datetime
from countershape.html import *
import countershape as cs
import testpages


class TestUL(testpages.DummyState):
    def test_one(self):
        u = UL(["one", "two", "three"])
        s = str(u)
        assert "three" in s

    def test_with_objects(self):
        u = UL([LI("one"), LI("two"), "three"])
        s = str(u)
        assert "two" in s
        assert "three" in s

    def test_withclass(self):
        u = UL(["one", "two", "three"], _class="testclass")
        s = str(u)
        assert "testclass" in s


class TestValue:
    def test_call(self):
        s = Value("foo")
        assert not s.value
        s = s(foo="one", bar="two")
        assert s.value == "one"
        assert str(s) == "one"

    def test_noarg(self):
        a = Value("foo")
        b = a()
        assert str(a) == str(b)


class TestGroup:
    def test_render(self):
        g = Group("foo", "bar")
        str(g)


class TestHalfTag:
    def test_makeAttrs(self):
        ht = HalfTag(
            "foo",
            one="two",
            two="!@#@#$#^%&&&**(&"
        )
        assert ht._makeAttrs()

    def test_makeAttrs_special(self):
        ht = HalfTag(
            "foo",
            _return="two",
            _class="!@#@#$#^%&&&**(&"
        )
        assert ht._makeAttrs()
        assert ht["return"]
        assert not ht.attrs.has_key("_return")

    def test_str(self):
        ht = HalfTag("foo", one="foo", two="bar")
        assert str(ht)

    def test_has_key(self):
        ht = HalfTag("foo", one="foo", two="bar")
        assert not ht.has_key("wibble")
        assert ht.has_key("one")

    def test_setattrs(self):
        ht = HalfTag("foo", id="bar")
        assert ht.id == "bar"

    def test_addClass(self):
        ht = HalfTag("foo", _class="foo")
        assert ht["class"] == "foo"
        ht.addCSSClass("bar")
        assert ht["class"] == "foo bar"
        ht = HalfTag("foo")
        assert not ht.has_key("class")
        ht.addCSSClass("bar")
        assert ht["class"] == "bar"


class TestFullTag(testpages.DummyState):
    def test_str(self):
        ft = FullTag("foo", "contents", one="foo", two="bar")
        assert str(ft)

    def test_nonzero(self):
        ft = FullTag("foo")
        assert bool(ft)

    def test_tree(self):
        s = DIV(
                DIV("", _class="one-one"),
                DIV(
                    DIV("", _class="one-two-one"),
                    DIV("", _class="one-two-two"),
                    _class="one-two"
                ),
                DIV("", _class="one-three"),
            )
        s = str(s)
        assert "one-two-two" in s

    def test_unicode(self):
        u = u"\u1234foober"
        s = DIV(u"\u1234foober")
        assert u in unicode(s)
