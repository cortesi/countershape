import model, doc

class Sitemap(model.BasePage, doc._DocMixin):
    structural = False
    def __init__(self, name):
        model.BasePage.__init__(self)
        self.name = name

    def __repr__(self):
        return "sitemap(%s)"%self.name

    def render(self, *args, **kwargs):
        return "test"
