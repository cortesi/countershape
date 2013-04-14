import os.path
import countershape
from countershape import model, markup
import testpages, tutils

class TestSyntax(testpages.DummyState):
    def test_simple_syntax(self):
        assert countershape.template.Syntax("py")("def foo")

    def test_syntax_withConf(self):
        p = countershape.template.Syntax(
                "py",
                style="emacs",
                linenos="inline",
                linenostep=5,
                cssClass="bar"
            )
        assert p("def foo")


class TestNS(testpages.DummyState):
    def setUp(self):
        self.d = countershape.doc.DocRoot(tutils.test_data.path("doctree"))
        self.application = countershape.doc.Doc(self.d)
        self.pageName = os.path.join(os.path.sep,"test.html")
        testpages.DummyState.setUp(self)

    def test_syntax_next(self):
        p = countershape.template._ns()["next"]
        assert p.title == "Test"

    def test_syntax_previous(self):
        p = countershape.template._ns()["previous"]
        assert not p


def test_cubescript():
    t = """
        @_!asdf!@
        $_!asdf!$
        <!--(_for foo in bar)-->
        <!--(_block bar)-->
    """
    out = countershape.template.cubescript(t)
    assert "@!asdf!@" in out
    assert "$!asdf!$" in out
    assert "<!--(for foo in bar)-->" in out
    assert "<!--(block bar)-->" in out


class TestTemplate(testpages.DummyState):
    def test_str(self):
        s = """
            top@!top!@top
            linkTo@!linkTo("TestPage")!@linkTo
            urlTo@!urlTo("TestPage")!@urlTo
            name@!this.name!@name
        """
        t = countershape.template.Template(False, s, this=countershape.state.page)
        s = str(t)
        assert "top.top" in s
        assert "linkTo<a href" in s
        assert "urlToTestPage" in s
        assert "nameTestPage" in s


class TestMarkdown(testpages.DummyState):
    def test_str(self):
        s = """name@!this.name!@name"""
        t = countershape.template.Template(markup.Markdown(), s, this=countershape.state.page)
        s = str(t)
        assert "TestPage" in s
        assert "<p>" in s

    def test_options(self):
        s = """__one__name@!this.name!@name"""
        t = countershape.template.Template(
                markup.Markdown(extras=["code-friendly"]),
                s,
                this=countershape.state.page
            )
        s = str(t)
        assert "__one__" in s


if markup.RST:
    class TestRst(testpages.DummyState):
        def test_str(self):
            s = """name@!this.name!@name"""
            t = countershape.template.Template(markup.RST(), s, this=countershape.state.page)
            s = str(t)
            assert "TestPage" in s
            assert "<p>" in s


class TestFileTemplate(testpages.DummyState):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot(
                [
                    testpages.TPageHTMLFileTemplate(),
                ]
            )
        )
        self.pageName = "TPageHTMLFileTemplate"
        testpages.DummyState.setUp(self)

    def test_foo(self):
        s = self.call("TPageHTMLFileTemplate")
        assert "nameTPageHTMLFileTemplatename" in s

