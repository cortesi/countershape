import html, template

class Layout:
    """
        A basic framework for layout objects.
    """
    dtd = '<!DOCTYPE html>\n'
    bodyClass = ""
    components = ("pageTitle", "body", "header")
    def __init__(self, path = None, **kwargs):
        if path:
            body = template.File(False, path)
        else:
            body = html.Value("body")
        meta = html.META(
                            content = "text/html; charset=utf-8"
                        )
        meta["http-equiv"] = "Content-Type"
        htmlBody = html.BODY(body, **kwargs)
        if self.bodyClass:
            htmlBody["class"] = self.bodyClass
        self.frame = html.Group(
                html.RawStr(self.dtd),
                html.HTML(
                    html.HEAD(
                        meta,
                        html.Value("header"),
                        html.TITLE(html.Value("pageTitle"))
                    ),
                    htmlBody,
                    xmlns = "http://www.w3.org/1999/xhtml",
                )
        )

    def __call__(self, page):
        data = {}
        for i in self.components:
            c = page._getLayoutComponent(i)
            data[i] = unicode(c)
        return self.frame(**data)


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
