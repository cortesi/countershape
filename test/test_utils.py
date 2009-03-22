from __future__ import with_statement

import os
import libpry
import countershape
import countershape.utils as utils

class uInDir(libpry.TmpDirMixin, libpry.AutoTree):
    def test_one(self):
        old = os.getcwd()
        with utils.InDir(self["tmpdir"]):
            assert os.getcwd() != old
        assert os.getcwd() == old


class uMakeURL(libpry.AutoTree):
    def test_page(self):
        assert utils.makeURL("foo", bar="voing", orc="foo") == "foo?bar=voing&orc=foo"
        assert utils.makeURL("foo") == "foo"

    def test_pageWithPath(self):
        assert utils.makeURL("foo/bar/voing") == "foo/bar/voing"
        assert utils.makeURL("foo/bar/voing", orc="foo") == "foo/bar/voing?orc=foo"

    def test_list(self):
        assert utils.makeURL("foo/bar/voing", foo=["one", "two"]) ==\
               "foo/bar/voing?foo=one&foo=two"

    def test_absolutePath(self):
        assert utils.makeURL("http://foo.bar.voing") == "http://foo.bar.voing"


class uUrlCat(libpry.AutoTree):
    def test_cat(self):
        assert utils.urlCat("foo", "bar") == "foo/bar"
        assert utils.urlCat("/foo", "bar") == "/foo/bar"
        assert utils.urlCat("/foo", "bar/") == "/foo/bar/"
        assert utils.urlCat("", "bar") == "bar"


class uisStringLike(libpry.AutoTree):
    def test_all(self):
        assert utils.isStringLike("foo")
        assert not utils.isStringLike([1, 2, 3])
        assert not utils.isStringLike((1, 2, 3))
        assert not utils.isStringLike(["1", "2", "3"])


class uisSequenceLike(libpry.AutoTree):
    def test_all(self):
        assert utils.isSequenceLike([1, 2, 3])
        assert utils.isSequenceLike((1, 2, 3))
        assert not utils.isSequenceLike("foobar")
        assert utils.isSequenceLike(["foobar", "foo"])
        x = iter([1, 2, 3])
        assert utils.isSequenceLike(x)


class uisNumeric(libpry.AutoTree):
    def test_all(self):
        assert utils.isNumeric(1)
        assert utils.isNumeric(1.1)
        assert not utils.isNumeric("a")
        assert not utils.isNumeric([])


class uWalkTree(libpry.AutoTree):
    def test_foo(self):
        s = set(utils.walkTree("doctree"))
        assert not "README" in s
        assert "copy" in s
        assert "foo/index.py" in s


class u_CaselessHelper(libpry.AutoTree):
    def test_hash(self):
        a = utils._CaselessHelper("Foo")
        b = utils._CaselessHelper("foo")
        d = {}
        d[a] = a
        d[b] = b
        assert len(d) == 1


class uMultiDict(libpry.AutoTree):
    def setUp(self):
        self.md = utils.MultiDict()

    def test_setget(self):
        self.md.append("foo", 1)
        assert self.md["foo"] == [1]

    def test_del(self):
        self.md.append("foo", 1)
        del self.md["foo"]
        assert not self.md.has_key("foo")

    def test_extend(self):
        self.md.append("foo", 1)
        self.md.extend("foo", [2, 3])
        assert self.md["foo"] == [1, 2, 3]

    def test_extend_err(self):
        self.md.append("foo", 1)
        libpry.raises("non-sequence", self.md.extend, "foo", 2)

    def test_get(self):
        self.md.append("foo", 1)
        self.md.append("foo", 2)
        assert self.md.get("foo") == [1, 2]
        assert self.md.get("bar") == None

    def test_caseSensitivity(self):
        self.md._helper = utils._CaselessHelper
        self.md["foo"] = [1]
        self.md.append("FOO", 2)
        assert self.md["foo"] == [1, 2]
        assert self.md["FOO"] == [1, 2]
        assert self.md.has_key("FoO")

    def test_dict(self):
        self.md.append("foo", 1)
        self.md.append("foo", 2)
        self.md["bar"] = [3]
        assert self.md == self.md
        assert dict(self.md) == self.md

    def test_setitem(self):
        libpry.raises(ValueError, self.md.__setitem__, "foo", "bar")
        self.md["foo"] = ["bar"]
        assert self.md["foo"] == ["bar"]

    def test_itemPairs(self):
        self.md.append("foo", 1)
        self.md.append("foo", 2)
        self.md.append("bar", 3)
        l = list(self.md.itemPairs())
        assert len(l) == 3
        assert ("foo", 1) in l
        assert ("foo", 2) in l
        assert ("bar", 3) in l


class uOrderedSet(libpry.AutoTree):
    def test_append(self):
        x = utils.OrderedSet()
        x.append(1)
        x.append(1)
        x.append(2)
        assert x == [1, 2]

    def test_extend(self):
        x = utils.OrderedSet()
        x.extend([1, 2, 2])
        assert x == [1, 2]

    def test_insert(self):
        x = utils.OrderedSet()
        x.insert(0, 2)
        x.insert(0, 2)
        x.insert(0, 1)
        assert x == [1, 2]

    def test_setitem(self):
        x = utils.OrderedSet()
        x.append(1)
        x[0] = 2
        assert x == [2]
        x.insert(0, 1)
        assert x == [1, 2]
        x[0] = 2
        assert x == [1, 2]


class uBufIter(libpry.AutoTree):
    def test_nop(self):
        l = [1, 2, 3]
        b = utils.BuffIter(l)
        assert list(b) == l

    def test_push(self):
        l = [1, 2, 3]
        b = utils.BuffIter(l)
        assert b.next() == 1
        b.push(1)
        assert b.next() == 1
        assert list(b) == [2, 3]


tests = [
    uMakeURL(),
    uUrlCat(),
    uisStringLike(),
    uisSequenceLike(),
    uisNumeric(),
    uWalkTree(),
    u_CaselessHelper(),
    uMultiDict(),
    uOrderedSet(),
    uBufIter(),
    uInDir(),
]


