import os.path
import sys
import argparse

import bottle
import livereload

from . import doc, blog, analysis, model


def make_app(root):
    app = bottle.Bottle()

    @app.route('<path:path>')
    def servestatic(path):
        idx = os.path.join(root, path.lstrip("/"), "index.html")
        print root, path, idx
        if os.path.exists(idx):
            return bottle.static_file(
                os.path.join(path, "index.html"),
                root=root
            )
        return bottle.static_file(path, root=root)

    return app


def main():
    parser = argparse.ArgumentParser(
        description = "Renders a Countershape documentation tree."
    )
    parser.add_argument(
        "-o", "--option", type=str,
        action="append", dest="options",
        default = [],
        help="Add option to document namespace."
    )
    parser.add_argument(
        "-d", "--dummy",
        action="store_true", dest="dummy", default=False,
        help="Perform a dummy run - don't render any files."
    )
    parser.add_argument(
        "-l", "--live",
        action="store_true", dest="live", default=False,
        help="Start a live server."
    )
    group = parser.add_argument_group("Analysis")
    group.add_argument(
        "-s", "--structure",
        action="store_true", dest="structure", default=False,
        help="Show site structure."
    )
    group.add_argument(
        "--blog-tags",
        action="store_true", dest="blogtags", default=False,
        help="Show blog tag histogram."
    )
    group.add_argument(
        "--blog-notags",
        action="store_true", dest="blognotags", default=False,
        help="Show blog posts with no tags."
    )
    group.add_argument(
        "--blog-has-option",
        action="store", type=str, dest="bloghasoption", default=False,
        help="Show blog posts with option."
    )
    group.add_argument(
        "--blog-has-no-option",
        action="store", type=str, dest="bloghasnooption", default=False,
        help="Show blog posts without option."
    )
    group.add_argument(
        "src",
        help="Source directory"
    )
    group.add_argument(
        "dst",
        help="Destination directory",
        nargs="?"
    )

    args = parser.parse_args()

    analysis_options = [
        "structure",
        "blogtags",
        "blognotags",
        "bloghasoption",
        "bloghasnooption"
    ]

    if any(getattr(args, i) for i in analysis_options):
        if args.dst:
            parser.error("Analysis options don't take a destination.")
    else:
        if not args.dst:
            parser.error("Render destination required.")
        if os.path.abspath(args.dst) == os.path.abspath(args.src):
            parser.error(
                "Refusing to render documentation source onto itself."
            )

    d = doc.Doc(args.src, args.options)
    if args.structure:
        d.root.dump()
    elif args.blogtags:
        analysis.blog_tags(d)
    elif args.blognotags:
        analysis.blog_notags(d)
    elif args.bloghasoption:
        analysis.blog_has_option(d, args.bloghasoption)
    elif args.bloghasnooption:
        analysis.blog_has_no_option(d, args.bloghasnooption)
    elif not args.dummy:
        def rerender():
            d = doc.Doc(args.src, args.options)
            print "RENDERING"
            try:
                d.render(args.dst)
            except model.ApplicationError, v:
                print >> sys.stderr, "Error in %s"%v.page.src
                print >> sys.stderr, "\t", v
                sys.exit(1)
            lst = filter(
                lambda x: isinstance(x, blog.Post), d.root.preOrder()
            )
            for i in lst:
                if i.changed:
                    print >> sys.stderr, "Rewriting %s"%i.src
                    i.rewrite()
        rerender()
        if args.live:
            app = make_app(os.path.abspath(args.dst))
            server = livereload.Server(app)
            server.watch(args.src, func=rerender)
            server.serve()
