
class Default:
    def __call__(self, s):
        return s


try:
    import markdown2
    class Markdown:
        def __init__(self, html4tags=False, tab_width=4, safe_mode=None, extras=None, link_patterns=None, use_file_vars=False):
            self.markdowner = markdown2.Markdown(
                html4tags,
                tab_width,
                safe_mode,
                extras,
                link_patterns,
                use_file_vars
            )

        def __call__(self, txt):
            return self.markdowner.convert(txt)
except ImportError: # pragma: no cover
    pass


try:
    import docutils.core
    class RST:
        def __call__(self, txt):
            d = docutils.core.publish_parts(txt, writer_name = "html4css1")
            return d["fragment"]
except ImportError: # pragma: no cover
    RST = None

