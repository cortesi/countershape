import cStringIO
import countershape
import countershape.model as model
import testpages, tutils


class TLayout(countershape.layout.Layout):
    bodyClass = "test"
    components = ("body", "header", "special")


class CMissingMethodLayout(testpages.TPageHTML):
    layout = TLayout(tutils.test_data.path("templates/frame.html"))


class CLayout(testpages.TPageHTML):
    layout = TLayout()
    def body(self):
        yield "body"

    def header(self):
        yield "header"

    def special(self):
        yield "special"


class FLayout(testpages.TPageHTML):
    layout = countershape.layout.FileLayout(tutils.test_data.path("templates/fileframe.html"))
    def body(self):
        yield "body"

    def header(self):
        yield "header"

    def special(self):
        yield "special"


class TestLayoutRender(testpages.RenderTester):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot([
                CMissingMethodLayout("missing"),
                CLayout("good"),
                FLayout("flayout"),
            ])
        )
        self.application.testing = 2

    def test_missingmethod(self):
        tutils.raises("cannot find layout component", self.call, "missing")

    def test_render(self):
        assert self.call("good")

    def test_render(self):
        assert self.call("flayout")


