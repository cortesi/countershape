import html
_dtd = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'

class Layout:
    """
        A basic framework for layout objects.
    """
    bodyClass = ""
    components = ("body", "header")
    def __init__(self, body=None):
        if not body:
            body = html.Value("body")
        meta = html.META(
                            content = "text/html; charset=utf-8"
                        )
        meta["http-equiv"] = "Content-Type"
        htmlBody = html.BODY(body)
        if self.bodyClass:
            htmlBody["class"] = self.bodyClass
        self.frame = html.Group(
                html.RawStr(_dtd),
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
