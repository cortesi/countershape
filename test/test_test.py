import libpry
import countershape, countershape.test
import testpages


class TestPage(countershape.Page):
    def run(self):
        yield "test"


class uRenderTester(countershape.test.RenderTester):
    def setUp(self):
        self.application = testpages.TestApplication(
            countershape.BaseRoot([
                testpages.TPage("top", structural=True),
                TestPage(),
            ])
        )

    def test_falsepage(self):
        assert self.call("TestPage") == "test"


tests = [
    uRenderTester()
]
