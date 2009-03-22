"""
    A Form is a tree of objects, with a Form object at the root.
"""
import html, model

class Link(html._Renderable):
    """
        A standard href link.
    """
    def __init__(self, destination):
        """
            The arguments are as follows:

                destination         Link destination (optional)
        """
        html._Renderable.__init__(self)
        self.destination = destination

    def __call__(self, valobj=None, **kwargs):
        return html._Renderable.__call__(self, valobj, **kwargs)

    def __str__(self):
        content = self.page.title or self.page.name
        vals = {}
        url = model.UrlTo(self.destination, **vals)
        return unicode(html.A(content, href=url))
