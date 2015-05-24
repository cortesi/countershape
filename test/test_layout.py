import cStringIO
import countershape
import countershape.model as model
import countershape.layout
import testpages, tutils


class FLayout(testpages.TPageHTML):
    layout = countershape.layout.FileLayout(
        tutils.test_data.path("templates/fileframe.html")
    )

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
                FLayout("flayout"),
            ])
        )
        self.application.testing = 2

    def test_render(self):
        assert self.call("good")

    def test_render(self):
        assert self.call("flayout")
