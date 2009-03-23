import libpry
import countershape, countershape.template
import countershape.doc


class TPage(countershape.Page):
    def __init__(self, name = None, structural = False, internal = False):
        if name:
            self.name = name
            self.title = name
        self.structural, self.internal = structural, internal
        countershape.Page.__init__(self)

    def run(self, *args, **kwargs):
        return str(args) + str(kwargs)


class TPageHTMLTemplate(countershape.HTMLPage):
    body = countershape.template.Template(False, "@!this.name!@")
    def __init__(self, name = None):
        if name:
            self.name = name
            self.title = name
        countershape.HTMLPage.__init__(self)


class TPageHTMLFileTemplate(countershape.HTMLPage):
    def __init__(self, name = None):
        if name:
            self.name = name
            self.title = name
        countershape.HTMLPage.__init__(self)

    def body(self):
        yield countershape.template.File(
                    False, "templates/TPageHTMLFileTemplate.html", this=self
            )


class TPageHTML(TPageHTMLTemplate):
    def body(self, *args, **kwargs):
        yield str(args) + str(kwargs)


class TPageNoLink(TPage):
    pass


class TPageWithTitle(TPage):
    title = "Tester"


class TestApplication(countershape.BaseApplication):
    testing = 1
    debug = 1
    scriptName = "foo"



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
                    countershape.model.BaseRoot(
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
            raise countershape.model.ApplicationError, p
        self.application.pre(p)

