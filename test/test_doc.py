import shutil, os
import countershape
from countershape import doc, model, sitemap
import testpages, tutils

class DocTestPage(doc._DocHTMLPage):
    def __init__(self, name):
        self.name = name
        doc._DocHTMLPage.__init__(self, name, name, dict(body=""), "bar")

    def body(self):
        yield self.name


class DummyPage(DocTestPage):
    def __init__(self):
        DocTestPage.__init__(self, "DummyPage")


class TestPython:
    def test_init(self):
        d = doc.PythonPage("name", "title", tutils.test_data.path("testmod/foo.py"))

    def test_repr(self):
        d = doc.PythonPage("name", "title", tutils.test_data.path("testmod/foo.py"))
        repr(d)

        m = doc.PythonModule(tutils.test_data.path("testmod"))
        repr(m)

    def test_index(self):
        d = doc.PythonModule("name", "title", tutils.test_data.path("testmod"))


class TestDocHTMLPage:
    def setUp(self):
        self.application = doc.Doc(
            TRoot([
                DummyPage()
            ])
        )

    def test_repr(self):
        repr(countershape.state.page)


class TestRenderTests:
    def setUp(self):
        self.application = doc.Doc(
            TRoot([
                doc.Page(tutils.test_data.path("doctree/test.html"), "Title"),
                doc.Copy(tutils.test_data.path("doctree/copy")),
                doc.Copy("copy2", src=tutils.test_data.path("doctree/copy")),
                doc.PythonPage(tutils.test_data.path("testmod/foo.py")),
                doc.PythonModule(tutils.test_data.path("testmod")),
                sitemap.Sitemap("sitemap.xml")
            ])
        )

    def test_render(self):
        with tutils.tmpdir() as t:
            self.application.render(t)
            assert os.path.isfile(os.path.join(t, "test.html"))
            assert os.path.isfile(os.path.join(t, "copy"))
            assert os.path.isfile(os.path.join(t, "copy2"))
            assert os.path.isdir(os.path.join(t, "testmod"))
            assert os.path.isfile(os.path.join(t, "testmod_index.html"))
            assert os.path.isfile(os.path.join(t, "sitemap.xml"))


class TestBunch:
    def test_load(self):
        l = doc._Bunch(a=1, b=2)
        assert l.a == 1
        l.c = 22
        assert l.getDict()["c"] == 22


class TestFullRender:
    def test_render(self):
        app = doc.Doc(tutils.test_data.path("doctree"))
        with tutils.tmpdir() as t:
            app.render(t)
            assert "notcopied" in app.root.namespace["data"]
            assert not os.path.isfile(os.path.join(t, "_notcopied.html"))
            assert os.path.isfile(os.path.join(t, "include.css"))
            assert os.path.isdir(os.path.join(t, "autocopy"))
            assert os.path.isdir(os.path.join(t, "foo"))

    def test_render_newdir(self):
        app = doc.Doc(tutils.test_data.path("doctree"))
        with tutils.tmpdir() as t:
            app.render(os.path.join(t, "newdir"))


class TestDocRoot:
    def test_render(self):
        tutils.raises(SyntaxError, doc.Doc, doc.DocRoot(tutils.test_data.path("doctree_err")))

    def test_repr(self):
        x = doc.DocRoot(tutils.test_data.path("doctree"))
        repr(x)


class TestPage(testpages.DummyState):
    def setUp(self):
        os.chdir(tutils.test_data.path("doctemplate"))
        self.d = doc.Page("test.html", "Title", pageTitle="PageTitle")
        self.application = doc.Doc(
            TRoot([
                self.d
            ])
        )
        self.application.testing = 2
        self.pageName = "test.html"
        testpages.DummyState.setUp(self)

    def tearDown(self):
        testpages.DummyState.tearDown(self)
        os.chdir("../..")

    def test_call(self):
        assert "mynameistest" in  self.application(self.d)

    def test_repr(self):
        repr(self.d)

    def test_getLayoutComponentErr(self):
        tutils.raises(
            "layout component \"nonexistent\"",
            self.d._getLayoutComponent,
            "nonexistent"
        )

    def test_getLayoutComponent(self):
        assert "mynameistest.html" in str(self.d._getLayoutComponent("body"))
        self.d.testAttr = "test"
        assert "test" == str(self.d._getLayoutComponent("testAttr"))

    def test_getLayoutComponent_pageTitle(self):
        assert str(self.d._getLayoutComponent("pageTitle")) == "PageTitle"
        self.application.root.titlePrefix = "prefix-"
        assert str(self.d._getLayoutComponent("pageTitle")) == "prefix-PageTitle"


    def test_namespace(self):
        self.d.namespace["foo"] = "bar"
        self.d._getNamespace()
        assert self.d.namespace["foo"] == "bar"
        assert self.d.namespace["body"].txt.strip() == "mynameis@!this.name!@"


def test_static_directory():
    s = doc.StaticDirectory("foo")
    repr(s)


def test_directory():
    s = doc.Directory(tutils.test_data.path("doctree"))
    repr(s)


class TestCopy(testpages.DummyState):
    def setUp(self):
        self.application = doc.Doc(
            TRoot([
                doc.Copy("bar", "foo")
            ])
        )
        self.pageName = "bar"
        testpages.DummyState.setUp(self)

    def test_repr(self):
        repr(countershape.state.page)


class TRoot(model.BaseRoot):
    contentName = "body"
    stdHeaders = []
    namespace = countershape.doc.DocRoot._baseNS
    site_url = "http://foo.com"


class TestOptions:
    def test_all(self):
        o = doc.Options(
            [
                "one",
                "three=four"
            ]
        )
        assert o.one
        assert not o.two
        assert o.three == "four"
        o.four = "five"
        assert o.four == "five"
        str(o)

