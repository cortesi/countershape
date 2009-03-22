"""
    A set of tools for testing applications.
"""
import libpry
import utils, countershape, model

class RenderTester(libpry.AutoTree):
    """
        This is a test strut for interacting with an application in test mode.
        It allows for rendering of pages, and a variety of tests for
        Redirection, errors, etc.

        In the setUp method of child classes, an Application should be
        instantiated and assigned to self.application.
    """
    application = None
    def tearDown(self):
        self.application.post(None)

    def call(self, spec):
        """
            Call a page, and return the resulting data.
                
                spec        - Either a string path, or a context object.
                **fields    - Field values
        """
        p = self.application.getPage(spec)
        if not p:
            raise countershape.ApplicationError, "No such page: %s"%spec
        self.application.pre(p)
        return "".join([unicode(i) for i in self.application(p)])


class TestPage(countershape.HTMLPage):
    def body(self):
        yield "dummy"


class DummyState(RenderTester):
    application = None
    pageName = None
    testing = 2
    def setUp(self):
        if not self.application:
            self.application = countershape.BaseApplication(
                    model.BaseRoot(
                        [
                            TestPage()
                        ]
                    )
            )
        self.application.testing = self.testing
        if not self.pageName:
            p = self.application.root.children[0]
        else:
            p = self.application.getPage(self.pageName)
        if not p:
            p = "Could not find test page."
            raise model.ApplicationError, p
        self.application.pre(p)

