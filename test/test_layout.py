import cStringIO
import libpry
import countershape
import countershape.model as model
import testpages


class TestLayout(countershape.layout.Layout):
    bodyClass = "test"
    components = ("body", "header", "special")


class CMissingMethodLayout(testpages.TPageHTML):
    layout = TestLayout("templates/frame.html")

class CLayout(testpages.TPageHTML):
    layout = TestLayout()
    def body(self):
        yield "body"

    def header(self):
        yield "header"

    def special(self):
        yield "special"


class uLayoutRender(testpages.RenderTester):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot([
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
