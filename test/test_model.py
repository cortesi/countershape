import shutil, time, cStringIO, os
import libpry
import countershape, testpages
from countershape import utils
from countershape import model
from countershape import state
import testpages


class uContext(testpages.DummyState):
    def setUp(self):
        testpages.DummyState.setUp(self)
        testpages.RenderTester.setUp(self)

    def test_relativePath(self):
        self.application = testpages.TestApplication(
            model.BaseRoot(
                [
                    testpages.TPageHTML("foo"), [
                        testpages.TPageHTML("bar")
                    ]
                ]
            )
        )
        p = self.application.getPage(os.path.join("foo","bar"))
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
        p = self.application.getPage(os.path.join("foo","bar"))
        assert p.top(), ".."


class uPageInstantiate(testpages.DummyState):
    def test_instantiate_err(self):
        self.application.testing = False
        libpry.raises("instantiated during page call", model.BasePage)


class uHeader(testpages.DummyState):
    def test_path(self):
        h = model.Header(state.page)
        h.path("foo.css")
        h.path("bar.js")
        assert "foo" in h._cssPath[0]
        assert "bar" in h._jsPath[0]

    def test_path_err(self):
        h = model.Header(state.page)
        libpry.raises("unrecognised resource extension", h.path, "foo.bar")

    def test_cssPath(self):
        h = model.Header(state.page)
        h.cssPath("foo")
        h.cssPath("bar")
        assert "foo" in h._cssPath[0]
        assert "bar" in h._cssPath[1]

    def test_jsPath(self):
        h = model.Header(state.page)
        h.jsPath("foo")
        h.jsPath("bar")
        assert "foo" in h._jsPath[0]
        assert "bar" in h._jsPath[1]

    def test_str(self):
        h = model.Header(state.page)
        h.cssPath("foo")
        h.cssPath("bar")
        h.jsPath("foo")
        h.jsPath("bar")
        s = str(h)
        assert len([i for i in s.splitlines() if i]) == 4
       

class uHTMLPage(testpages.RenderTester):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot(
                [
                    testpages.TPageHTMLFileTemplate(),
                    [
                        testpages.TPageHTML("nestedpage")
                    ],
                    testpages.TPageHTMLTemplate(),
                ]
            )
        )
        self.application.testing = 2

    def test_pageTitle(self):
        t = testpages.TPageHTMLTemplate()
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

    def test_repr(self):
        t = testpages.TPageHTMLTemplate()
        assert repr(t)


class uBaseApplication(testpages.RenderTester):
    def setUp(self):
        self.r = model.BaseRoot(
            [
                TException("one"),
            ]
        )
        self.application = model.BaseApplication(self.r)

    def test_pageexception(self):
        p = self.application.getPage("one")
        libpry.raises("an exception", self.application, p)


class uApplication(testpages.DummyState):
    def setUp(self):
        self.application = testpages.TestApplication(
           model.BaseRoot(
                [
                    testpages.TPageHTML("base"),
                    [
                        testpages.TPageNoLink(),
                        testpages.TPageWithTitle()
                    ],
                    testpages.TPage("internal", internal=True)
                ]
            )
        )
        self.pageName = "base"
        testpages.DummyState.setUp(self)

    def test_getPageErr(self):
        assert not self.application.getPage('nonexistent')
        libpry.raises("invalid argument", self.application.getPage, 0)

    def test_getPageIdempotence(self):
        p = self.application.getPage('base')
        assert self.application.getPage(p) == p

    def test_getPageRoot(self):
        assert self.application.getPage("").name == "BaseRoot"

    def test_LinkTo(self):
        assert str(model.LinkTo("base"))
        assert model.LinkTo("base")()

    def test_linkTo_withTitle(self):
        assert str(model.LinkTo("TPageWithTitle"))

    def test_linkTo_nopage(self):
        libpry.raises(
            "unknown page",
            str,
            model.LinkTo("Nonexistent")
        )

    def test_linkTo_nolink(self):
        assert str(model.LinkTo("TPageNoLink"))

    def test_url(self):
        assert str(model.UrlTo("TPageNoLink"))

    def test_url_anchor(self):
        s = str(model.UrlTo("TPageNoLink", anchor="foo"))
        assert s == "base/TPageNoLink#foo"

    def test_url_nopage(self):
        libpry.raises("unknown page", str, model.UrlTo("Nonexistent"))

    def test_url_internal(self):
        libpry.raises("internal page", str, model.UrlTo("internal"))

    def test_alink(self):
        s = str(model.ALink("TPageNoLink", "text", "foo"))
        assert  "TPageNoLink#foo" in s

    def test_linkTo_internal(self):
        libpry.raises(
            model.ApplicationError,
            str,
            model.LinkTo("internal")
        )


class uPageModel(libpry.AutoTree):
    """
        A suite of tests testing the application page model functionality.
        Tests span the Application and Page classes.
    """
    def setUp(self):
        state.page = None
        self.a, self.b = testpages.TPage("test"), testpages.TPage("test")
        self.s1, self.s2 = testpages.TPage("end", structural=True), testpages.TPage("end", structural=True)
        self.p1, self.p2 = testpages.TPage("sub1", structural=True), testpages.TPage("sub2", structural=True)
        self.r = model.BaseRoot([
                testpages.TPage("base", structural=False, internal=True),[
                    self.a,
                    testpages.TPage("one", structural=True), [
                        testpages.TPage("X", structural=False),[
                            testpages.TPage("two", structural=True, internal=False), [
                                self.b,
                            ]
                        ]
                    ],
                    self.p1, [
                        testpages.TPage("page", structural=True), [
                            self.s1
                        ],
                    ],
                    self.p2, [
                        testpages.TPage("page", structural=True), [
                            self.s2,
                        ]
                    ],
                ]
            ])
        self.t = testpages.TestApplication(self.r)
        state.application = self.t

    def tearDown(self):
        state.ctx = None

    def test_getPage(self):
        libpry.raises("ambiguous path", self.t.getPage, os.path.join("page","end"))
        assert self.t.getPage(os.path.join("sub1","page","end"))
        assert self.t.getPage(os.path.join("sub2","page","end"))

    def test_getPageChild(self):
        state.page = self.p1
        assert self.t.getPage(os.path.join(".","page","end")) is self.s1
        assert not self.t.getPage(os.path.join(".","page","foo"))
        assert self.t.getPage(os.path.join(".","page"))

    def test_getPage_nostate(self):
        libpry.raises("relative page link", self.t.getPage, os.path.join(".","page","end"))

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
        assert not self.r.matchPage(["page"], False)

    def test_root_url(self):
        state.page = self.t.getPage(os.path.join("one","two"))
        assert str(model.UrlTo("BaseRoot")) == ".."

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
        state.page = self.t.getPage(os.path.join("one","two"))
        assert str(model.UrlTo("two")) == "two"
        state.page = self.t.getPage("one")
        assert str(model.UrlTo("one")) == "one"


class uPage(libpry.AutoTree):
    def test_isDocDescendantOf(self):
        one = testpages.TPage("one")
        two = testpages.TPage("two")
        r = model.BaseRoot(
                [
                    one,
                    testpages.TPage("dir", internal=True), [
                        two
                    ]
                ]
            )
        t = testpages.TestApplication(r)
        assert not two.isDescendantOf(one)
        assert two.isDocDescendantOf(one)
        assert two.isDocDescendantOf(r)
        assert r.isDescendantOf(two)


class uPageModelErrors(libpry.AutoTree):
    def test_ambiguouschild(self):
        r = model.BaseRoot([
            testpages.TPage("one", structural=True), [
                testpages.TPage("test"),
                testpages.TPage("test"),
            ]
        ])
        libpry.raises(
            model.ApplicationError,
            testpages.TestApplication,
            r
        )

    def test_ambiguouschild2(self):
        r = model.BaseRoot([
            testpages.TPage("one", structural=True), [
                testpages.TPage("test"),
                testpages.TPage("X", structural=False),[
                    testpages.TPage("test"),
                ]
            ]
        ])
        libpry.raises(
            model.ApplicationError,
            testpages.TestApplication,
            r
        )

    def test_ambiguoustoplevel(self):
        r = model.BaseRoot([
            testpages.TPage("test", structural=True),
            testpages.TPage("test", structural=False),
        ])
        libpry.raises(
            model.ApplicationError,
            testpages.TestApplication,
            r
        )


class TException(testpages.TPage):
    def render(self, *args, **kwargs):
        raise ValueError("An exception")


_TestApp = testpages.TestApplication(
    model.BaseRoot(
        [
            testpages.TPage("one", structural=True),
            [
                testpages.TPage("two"),
                testpages.TPage("three")
            ],
            testpages.TPage("internal", internal=True),
            TException("exception"),
        ]
    )
)


class uApplicationRenderNoTesting(testpages.RenderTester):
    def setUp(self):
        self.application = _TestApp
        self.application.testing = 1
        testpages.RenderTester.setUp(self)

    def test_dirtystate(self):
        self.application.testing = 0
        self.application.debug = 1
        io = cStringIO.StringIO()
        self.application.logErr = io
        p = model.BasePage()
        libpry.raises("Dirty state", self.application.pre, p)

    def test_prenotesting(self):
        self.application.testing = 0
        p = model.BasePage()
        self.application.pre(p)


class uApplicationRender(testpages.RenderTester):
    def setUp(self):
        self.application = _TestApp
        self.application.testing = 2

    def test_call(self):
        assert self.call("one")

    def test_call_nonexistent(self):
        libpry.raises(model.ApplicationError, self.call, "nonexistent")


class uApplicationError(libpry.AutoTree):
    def test_str(self):
        a = model.ApplicationError("foo")
        str(a)


tests = [
    uPage(),
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

