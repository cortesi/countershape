import countershape, countershape.template
import countershape.doc, countershape.test

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
