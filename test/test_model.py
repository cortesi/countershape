import shutil, time, cStringIO
import libpry
import countershape, countershape.test
from countershape import *
from countershape import utils
from testpages import *


class uContext(countershape.test.DummyState):
    def setUp(self):
        countershape.test.DummyState.setUp(self)
        countershape.test.RenderTester.setUp(self)

    def test_relativePath(self):
        self.application = TestApplication(
            AppRoot(
                [
                    TPageHTML("foo"), [
                        TPageHTML("bar")
                    ]
                ]
            )
        )
        p = self.application.getPage("foo/bar")
        assert p.relativePath(["oink"]) == "../oink"
        assert p.relativePath(["oink", "voing"]) == "../oink/voing"
        assert p.relativePath(["foo"]) == "../foo"
        assert p.relativePath([]) == ".."
        assert p.relativePath(["foo", "bar"]) == "bar"
        assert p.relativePath(["foo", "bar", "voing"]) == "bar/voing"

        p = self.application.getPage("foo")
        assert p.relativePath(["oink"]) == "oink"
        assert p.relativePath([""]) == ""
        assert p.relativePath(["foo", "bar"]) == "foo/bar"

    def test_top(self):
        p = self.application.getPage("foo/bar")
        assert p.top(), ".."


class uPageInstantiate(test.DummyState):
    def test_instantiate_err(self):
        self.application.testing = False
        libpry.raises("instantiated during page call", Page)


class uHeader(test.DummyState):
    def test_cssPath(self):
        h = Header(state.page)
        h.cssPath("foo")
        h.cssPath("bar")
        assert "foo" in h._cssPath[0]
        assert "bar" in h._cssPath[1]

    def test_jsPath(self):
        h = Header(state.page)
        h.jsPath("foo")
        h.jsPath("bar")
        assert "foo" in h._jsPath[0]
        assert "bar" in h._jsPath[1]

    def test_str(self):
        h = Header(state.page)
        h.cssPath("foo")
        h.cssPath("bar")
        h.jsPath("foo")
        h.jsPath("bar")
        s = str(h)
        assert len([i for i in s.splitlines() if i]) == 4
       

class uHTMLPage(countershape.test.RenderTester):
    def setUp(self):
        self.application = TestApplication(
            AppRoot(
                [
                    TPageHTMLFileTemplate(),
                    [
                        TPageHTML("nestedpage")
                    ],
                    TPageHTMLTemplate(),
                ]
            )
        )
        self.application.testing = 2

    def test_pageTitle(self):
        t = TPageHTMLTemplate()
        assert t.pageTitle() == "TPageHTMLTemplate"
        t.title = "Foo"
        assert t.pageTitle() == "Foo"
        t.pageTitle = "Bar"
        assert t.pageTitle == "Bar"

    def test_template(self):
        d = self.call("TPageHTMLTemplate")
        assert d.find("html") > -1
        assert d.find("TPageHTMLTemplate") > -1

    def test_filetemplate(self):
        d = self.call("TPageHTMLFileTemplate")
        assert d.find("template") > -1
        assert d.find("html") > -1


class uBaseApplication(test.RenderTester):
    def setUp(self):
        self.r = AppRoot(
            [
                TException("one"),
            ]
        )
        self.application = BaseApplication(self.r)

    def test_pageexception(self):
        p = self.application.getPage("one")
        libpry.raises("an exception", list, self.application(p))


class uApplication(test.DummyState):
    def setUp(self):
        self.application = TestApplication(
           AppRoot(
                [
                    TPageHTML("base"),
                    [
                        TPageNoLink(),
                        TPageWithTitle()
                    ],
                    TPage("internal", internal=True)
                ]
            )
        )
        self.pageName = "base"
        test.DummyState.setUp(self)

    def test_getPageErr(self):
        assert not self.application.getPage('nonexistent')
        libpry.raises("invalid argument", self.application.getPage, 0)

    def test_getPageIdempotence(self):
        p = self.application.getPage('base')
        assert self.application.getPage(p) == p

    def test_getPageRoot(self):
        assert self.application.getPage("").name == "AppRoot"

    def test_LinkToNoArgs(self):
        assert str(LinkTo("base"))

    def test_linkTo_withTitle(self):
        assert str(LinkTo("TPageWithTitle"))

    def test_linkTo_nopage(self):
        libpry.raises(
            "unknown page",
            str,
            LinkTo("Nonexistent")
        )

    def test_linkTo_nolink(self):
        assert str(LinkTo("TPageNoLink"))

    def test_url(self):
        assert str(UrlTo("TPageNoLink"))

    def test_url_anchor(self):
        s = str(UrlTo("TPageNoLink", anchor="foo"))
        assert s == "base/TPageNoLink#foo"

    def test_url_nopage(self):
        libpry.raises("unknown page", str, UrlTo("Nonexistent"))

    def test_url_internal(self):
        libpry.raises("internal page", str, UrlTo("internal"))

    def test_alink(self):
        s = str(ALink("TPageNoLink", "text", "foo"))
        assert  "TPageNoLink#foo" in s

    def test_linkTo_internal(self):
        libpry.raises(
            countershape.ApplicationError,
            str,
            LinkTo("internal")
        )


class uPageModel(libpry.AutoTree):
    """
        A suite of tests testing the application page model functionality.
        Tests span the Application and Page classes.
    """
    def setUp(self):
        state.page = None
        self.a, self.b = TPage("test"), TPage("test")
        self.s1, self.s2 = TPage("end", structural=True), TPage("end", structural=True)
        self.p1, self.p2 = TPage("sub1", structural=True), TPage("sub2", structural=True)
        self.r = AppRoot([
                TPage("base", structural=False, internal=True),[
                    self.a,
                    TPage("one", structural=True), [
                        TPage("X", structural=False),[
                            TPage("two", structural=True, internal=False), [
                                self.b,
                            ]
                        ]
                    ],
                    self.p1, [
                        TPage("page", structural=True), [
                            self.s1
                        ],
                    ],
                    self.p2, [
                        TPage("page", structural=True), [
                            self.s2,
                        ]
                    ],
                ]
            ])
        self.t = TestApplication(self.r)
        state.application = self.t

    def tearDown(self):
        state.ctx = None

    def test_getPage(self):
        libpry.raises("ambiguous path", self.t.getPage, "page/end")
        assert self.t.getPage("sub1/page/end")
        assert self.t.getPage("sub2/page/end")

    def test_getPageChild(self):
        state.page = self.p1
        assert self.t.getPage("./page/end") is self.s1
        assert not self.t.getPage("./page/foo")
        assert self.t.getPage("./page")

    def test_getPage_nostate(self):
        libpry.raises("relative page link", self.t.getPage, "./page/end")

    def test_getPageParent(self):
        state.page = self.s1
        assert self.t.getPage("^/page") is self.p1.children[0]
        assert self.t.getPage("^/sub1") is self.p1

    def test_getPageSibling(self):
        state.page = self.p1
        assert self.t.getPage("-/sub2") is self.p2
        assert not self.t.getPage("-/page")

    def test_getPageLocal(self):
        state.page = self.p1
        assert self.t.getPage("$/sub2") is self.p2
        assert self.t.getPage("$/base")
        assert not self.t.getPage("$/X")

    def test_matchPage(self):
        assert self.b.matchPage([], False)
        assert self.b.matchPage(["two"], False)
        assert self.b.matchPage(["one", "two"], False)
        assert not self.b.matchPage(["two", "two"], False)
        assert self.s1.matchPage(["sub1", "page"], False)
        assert self.s1.matchPage(["page"], False)
        assert self.s2.matchPage(["page"], False)

        assert self.s1.matchPage(["sub1", "page"], True)
        assert not self.s1.matchPage(["page"], True)

    def test_root_url(self):
        state.page = self.t.getPage("one/two")
        assert str(UrlTo("AppRoot")) == ".."

    def test_getPath(self):
        page, path = self.t.getPath(["one", "two"])
        assert page.name == "two"
        assert path == []

        page, path = self.t.getPath(["one"])
        assert page.name == "one"
        assert path == []

        page, path = self.t.getPath(["one", "argument"])
        assert page.name == "one"
        assert path == ["argument"]

        page, path = self.t.getPath(["test"])
        assert page.name == "test"
        assert path == []

        assert self.t.getPath([]) == (self.r, [])
        assert self.t.getPath(["piglet"]) == (self.r, ["piglet"])
        assert self.t.getPath(["two", "foo"]) == (self.r, ["two", "foo"])

    def test_url(self):
        state.page = self.t.getPage("one/two")
        assert str(UrlTo("two")) == "two"
        state.page = self.t.getPage("one")
        assert str(UrlTo("one")) == "one"


class uPageModelErrors(libpry.AutoTree):
    def test_ambiguouschild(self):
        r = AppRoot([
            TPage("one", structural=True), [
                TPage("test"),
                TPage("test"),
            ]
        ])
        libpry.raises(
            countershape.ApplicationError,
            TestApplication,
            r
        )

    def test_ambiguouschild2(self):
        r = AppRoot([
            TPage("one", structural=True), [
                TPage("test"),
                TPage("X", structural=False),[
                    TPage("test"),
                ]
            ]
        ])
        libpry.raises(
            countershape.ApplicationError,
            TestApplication,
            r
        )

    def test_ambiguoustoplevel(self):
        r = AppRoot([
            TPage("test", structural=True),
            TPage("test", structural=False),
        ])
        libpry.raises(
            countershape.ApplicationError,
            TestApplication,
            r
        )


class TException(TPage):
    def __call__(self, *args, **kwargs):
        raise ValueError("An exception")


_TestApp = TestApplication(
    AppRoot(
        [
            TPage("one", structural=True),
            [
                TPage("two"),
                TPage("three")
            ],
            TPage("internal", internal=True),
            TException("exception"),
        ]
    )
)


class uApplicationRenderNoTesting(test.RenderTester):
    def setUp(self):
        self.application = _TestApp
        self.application.testing = 1
        test.RenderTester.setUp(self)

    def test_dirtystate(self):
        self.application.testing = 0
        self.application.debug = 1
        io = cStringIO.StringIO()
        self.application.logErr = io
        p = countershape.Page()
        libpry.raises("Dirty state", self.application.pre, p)

    def test_prenotesting(self):
        self.application.testing = 0
        p = countershape.Page()
        self.application.pre(p)


class uApplicationRender(test.RenderTester):
    def setUp(self):
        self.application = _TestApp
        self.application.testing = 2

    def test_call(self):
        assert self.call("one")

    def test_call_nonexistent(self):
        libpry.raises(countershape.ApplicationError, self.call, "nonexistent")


class uApplicationError(libpry.AutoTree):
    def test_str(self):
        a = countershape.ApplicationError("foo")
        str(a)


tests = [
    uPageInstantiate(),
    uHeader(),
    uHTMLPage(),
    uBaseApplication(),
    uApplication(),
    uPageModel(),
    uPageModelErrors(),
    uApplicationRenderNoTesting(),
    uApplicationRender(),
    uApplicationError(),
    uContext(),
]

