import model, doc, state, template, utils

class Sitemap(model.BasePage, doc._DocMixin):
    structural = False
    def __init__(self, name):
        model.BasePage.__init__(self)
        self.name = name
        self.absolute_domain = True

    def __repr__(self):
        return "sitemap(%s)"%self.name

    def render(self, *args, **kwargs):
        pages = []
        for i in state.application.root.preOrder():
            if i.structural and not i.internal:
                pages.append(i)
        t = template.Template(
                None,
                file(utils.data.path("resources/sitemap.xml")).read(),
                pages = pages
            )
        return unicode(t)
