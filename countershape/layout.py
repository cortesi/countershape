from . import template, utils


class FileLayout:
    """
        A framework for layout objects, sourced from a file.
    """
    components = ("pageTitle", "body", "header")

    def __init__(self, path = None, **kwargs):
        self.layout = template.File(False, path)

    def __call__(self, page):
        data = {}
        for i in self.components:
            c = page._getLayoutComponent(i)
            data[i] = unicode(c)
        return self.layout(**data)


DefaultLayout = FileLayout(utils.data.path("resources/default_layout.html"))
