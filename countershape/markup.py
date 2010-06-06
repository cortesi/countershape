
class Default:
    def __call__(self, s):
        return s


#begin nocover
try:
    import markdown2
    class Markdown:
        def __init__(self):
            self.markdowner = markdown2.Markdown()
        
        def __call__(self, txt):
            return self.markdowner.convert(txt)
except ImportError:
    pass
#end nocover


#begin nocover
try:
    import docutils.core
    class RST:
        def __call__(self, txt):
            d = docutils.core.publish_parts(txt, writer_name = "html4css1")
            return d["fragment"]
except ImportError:
    pass
#end nocover

