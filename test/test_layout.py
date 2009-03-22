import cStringIO
import libpry
import countershape
import testpages


class TestLayout(countershape.layout.Layout):
    components = ("body", "inline", "header", "special")

class CMissingMethodLayout(testpages.TPageHTML):
    layout = TestLayout()


class CLayout(testpages.TPageHTML):
    layout = TestLayout()
    def body(self):
        yield "body"

    def inline(self):
        yield "inline"

    def header(self):
        yield "header"

    def special(self):
        yield "special"


class uLayoutRender(countershape.test.RenderTester):
    def setUp(self):
        self.application = testpages.TestApplication(
            countershape.BaseRoot([
                CMissingMethodLayout("missing"),
                CLayout("good"),
            ])
        )
        self.application.testing = 2

    def test_missingmethod(self):
        libpry.raises("cannot find layout component", self.call, "missing")

    def test_render(self):
        assert self.call("good")


tests = [
    uLayoutRender()
]
