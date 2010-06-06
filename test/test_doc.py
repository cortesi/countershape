import shutil, os
import libpry
import countershape
import countershape.doc as doc
import countershape.model as model
import testpages

class DocTestPage(doc._DocHTMLPage):
    def __init__(self, name):
        self.name = name
        doc._DocHTMLPage.__init__(self, name, name, dict(body=""), "bar")

    def body(self):
        yield self.name


class DummyPage(DocTestPage):
    def __init__(self):
        DocTestPage.__init__(self, "DummyPage")


class uPython(libpry.AutoTree):
    def test_init(self):
        d = doc.PythonPage("name", "title", "testmod/foo.py")

    def test_repr(self):
        d = doc.PythonPage("name", "title", "testmod/foo.py")
        repr(d)

        m = doc.PythonModule("testmod")
        repr(m)

    def test_index(self):
        d = doc.PythonModule("name", "title", "testmod")


class u_DocHTMLPage(libpry.AutoTree):
    def setUp(self):
        self.application = doc.Doc(
            TestRoot([
                DummyPage()
            ])
        )

    def test_repr(self):
        repr(countershape.state.page)


class uRenderTests(libpry.AutoTree):
    def setUp(self):
        self.application = doc.Doc(
            TestRoot([
                doc.Page("doctree/test.html", "Title"),
                doc.Copy("doctree/copy"),
                doc.Copy("copy2", src="doctree/copy"),
                doc.PythonPage("testmod/foo.py"),
                doc.PythonModule("testmod")
            ])
        )

    def test_render(self):
        t = self.tmpdir()
        self.application.render(t)
        assert os.path.isfile(os.path.join(t, "test.html"))
        assert os.path.isfile(os.path.join(t, "copy"))
        assert os.path.isfile(os.path.join(t, "copy2"))
        assert os.path.isdir(os.path.join(t, "testmod"))
        assert os.path.isfile(os.path.join(t, "testmod_index.html"))

class uBunch(libpry.AutoTree):
    def test_load(self):
        l = doc._Bunch(a=1, b=2)
        assert l.a == 1
        l.c = 22
        assert l.getDict()["c"] == 22


class uFullRender(libpry.AutoTree):
    def test_render(self):
        app = doc.Doc("doctree")
        t = self.tmpdir()
        app.render(t)
        assert "notcopied" in app.root.namespace["data"]
        assert not os.path.isfile(os.path.join(t, "_notcopied.html"))
        assert os.path.isfile(os.path.join(t, "include.css"))
        assert os.path.isdir(os.path.join(t, "autocopy"))
        assert os.path.isdir(os.path.join(t, "foo"))

    def test_render_newdir(self):
        app = doc.Doc("doctree")
        t = self.tmpdir()
        app.render(os.path.join(t, "newdir"))


class uDocRoot(libpry.AutoTree):
    def test_render(self):
        libpry.raises(SyntaxError, doc.Doc, doc.DocRoot("doctree_err"))

    def test_repr(self):
        x = doc.DocRoot("doctree")
        repr(x)


class uPage(testpages.DummyState):
    def setUp(self):
        os.chdir("doctemplate")
        self.d = doc.Page("test.html", "Title", pageTitle="PageTitle")
        self.application = doc.Doc(
            TestRoot([
                self.d
            ])
        )
        self.application.testing = 2
        self.pageName = "test.html"
        testpages.DummyState.setUp(self)

    def tearDown(self):
        testpages.DummyState.tearDown(self)
        os.chdir("..")

    def test_call(self):
        assert "mynameistest" in  self.application(self.d)

    def test_repr(self):
        repr(self.d)

    def test_getLayoutComponentErr(self):
        libpry.raises(
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


class uStaticDirectory(libpry.AutoTree):
    def test_repr(self):
        s = doc.StaticDirectory("foo")
        repr(s)


class uDirectory(libpry.AutoTree):
    def test_repr(self):
        s = doc.Directory("doctree")
        repr(s)


class uCopy(testpages.DummyState):
    def setUp(self):
        self.application = doc.Doc(
            TestRoot([
                doc.Copy("bar", "foo")
            ])
        )
        self.pageName = "bar"
        testpages.DummyState.setUp(self)

    def test_repr(self):
        repr(countershape.state.page)


class TestRoot(model.BaseRoot):
    contentName = "body"
    stdHeaders = []
    namespace = countershape.doc.DocRoot._baseNS


class uOptions(libpry.AutoTree):
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


tests = [
    uPython(),
    uStaticDirectory(),
    uDirectory(),
    u_DocHTMLPage(),
    uPage(),
    uCopy(),
    uRenderTests(),
    uFullRender(),
    uBunch(),
    uDocRoot(),
    uOptions()


]
