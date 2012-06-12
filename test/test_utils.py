import os
import countershape
import countershape.utils as utils
import tutils

class TestInDir:
    def test_one(self):
        with tutils.tmpdir() as t:
            old = os.getcwd()
            sub = os.path.join(t, "sub")
            os.mkdir(sub)
            with utils.InDir(sub):
                assert os.getcwd() != old
            assert os.getcwd() == old


class TestMakeURL:
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


def test_urlCat():
    assert utils.urlCat("foo", "bar") == "foo/bar"
    assert utils.urlCat("/foo", "bar") == "/foo/bar"
    assert utils.urlCat("/foo", "bar/") == "/foo/bar/"
    assert utils.urlCat("", "bar") == "bar"


def test_isStringLike():
    assert utils.isStringLike("foo")
    assert not utils.isStringLike([1, 2, 3])
    assert not utils.isStringLike((1, 2, 3))
    assert not utils.isStringLike(["1", "2", "3"])


def test_isSequenceLike():
    assert utils.isSequenceLike([1, 2, 3])
    assert utils.isSequenceLike((1, 2, 3))
    assert not utils.isSequenceLike("foobar")
    assert not utils.isSequenceLike(1)
    assert utils.isSequenceLike(["foobar", "foo"])
    x = iter([1, 2, 3])
    assert utils.isSequenceLike(x)


def test_isNumeric():
    assert utils.isNumeric(1)
    assert utils.isNumeric(1.1)
    assert not utils.isNumeric("a")
    assert not utils.isNumeric([])


def test_walkTree():
    s = set(utils.walkTree(tutils.test_data.path("doctree")))
    assert not "README" in s
    assert "copy" in s
    assert os.path.join("foo","index.py") in s


class TestOrderedSet:
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


class TestBufIter:
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

