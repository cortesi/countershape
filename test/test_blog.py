import datetime, os, shutil
import countershape
import countershape.test as test
import countershape.doc as doc
import libpry
import countershape.blog as blog

class TestRoot(countershape.BaseRoot):
    contentName = "body"
    stdHeaders = []
    namespace = countershape.doc._DocRoot._baseNS


class uPost(libpry.AutoTree):
    def setUp(self):
        self.post = self.getPost()

    def test_repr(self):
        repr(self.post)

    def getPost(self):
        return blog.Post("blogpages/testpost")

    def test_cmp(self):
        p = self.getPost()
        p2 = self.getPost()
        assert p != p2

    def test_fromStr(self):
        data = """
            my title
            time: 1977-11-24 14:05
            short: this is the 
            short description
            of this post

            this
            is
            data
        """
        title, time, data, short = blog.Post.fromStr(data)
        assert title == "my title"
        assert time == datetime.datetime(1977, 11, 24, 14, 05)
        d = data.strip()
        assert d.startswith("this")
        assert d.endswith("data")
        d = short.strip()
        assert d.startswith("this is the")
        assert d.endswith("this post")

    def test_fromStr_err(self):
        libpry.raises("not a valid post", blog.Post.fromStr, "")
        libpry.raises("invalid metadata", blog.Post.fromStr, "title\nmetadata")
        libpry.raises("invalid metadata", blog.Post.fromStr, "title\nmetadata: foo")

    def test_fromPath(self):
        title, time, data, short = blog.Post.fromPath("testblog/postone")
        assert title == "Title One"
        assert short == "multi\nline\nshort"

    def test_timeToStr(self):
        time = datetime.datetime(1977, 11, 24, 14, 05)
        assert self.post._timeToStr(time) == "1977-11-24 14:05"

    def test_toStr(self):
        s = self.post.toStr()
        title, time, data, short = blog.Post.fromStr(s)
        assert self.post.short == short
        assert self.post.title == title
        assert self.post.time == time
        assert self.post.data == data

    def test_toStr_noshort(self):
        p = blog.Post("blogpages/testpost_noshort")
        title, time, data, short = blog.Post.fromStr(p.toStr())
        assert p.short == short
        assert p.title == title
        assert p.time == time
        assert p.data == data


class uRewriteTests(libpry.TmpDirMixin, libpry.AutoTree):
    def setUp(self):
        libpry.TmpDirMixin.setUp(self)
        self.bdir = os.path.join(self["tmpdir"], "blog")
        shutil.copytree("testblog", self.bdir)

    def test_rewrite(self):
        post = blog.Post(os.path.join(self.bdir, "posthree"))
        assert post.changed
        post.rewrite()
        post = blog.Post(os.path.join(self.bdir, "posthree"))
        assert not post.changed


class uBlogDirectory(libpry.AutoTree):
    def test_init(self):
        a = doc._DocApplication(
                TestRoot(
                    [
                        blog.BlogDirectory("testblog")
                    ]
                )
            )
        #a.root.dump()


class uBlog(libpry.TmpDirMixin, libpry.AutoTree):
    def setUp(self):
        libpry.TmpDirMixin.setUp(self)
        self.b = blog.Blog("Blog Title", "blog description", "http://foo", "posts", "testblog")
        self.a = doc._DocApplication(
                TestRoot(
                    [
                        self.b(),
                        self.b.index("index.html", "Blog"),
                        self.b.archive("name.html", "Title"),
                        self.b.rss("rss.xml", "RS"),
                    ]
                )
            )

    def test_render(self):
        self.a.render(self["tmpdir"])

    def test_call(self):
        assert self.b()

    def test_archive_repr(self):
        a = self.b.archive("name", "my title")
        repr(a)

    def test_archive(self):
        a = self.b.archive("name", "my title")
        assert a.name == "name"
        assert a.title == "my title"
        a._getArchive()

    def test_index(self):
        a = self.b.index("name", "my title")
        assert a.name == "name"
        assert a.title == "my title"
        a._getIndex()

    def test_index_repr(self):
        a = self.b.index("name", "my title")
        repr(a)

    def test_rss(self):
        a = self.b.rss("name", "my title")
        assert a.name == "name"
        assert a.title == "my title"

    def test_rss_repr(self):
        a = self.b.rss("name", "my title")
        repr(a)


tests = [
    uPost(),
    uBlogDirectory(),
    uBlog(),
    uRewriteTests()
]
