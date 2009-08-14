import datetime, os, shutil
import countershape
import countershape.model as model
import countershape.doc as doc
import countershape.blog as blog
import libpry

class TestRoot(model.BaseRoot):
    contentName = "body"
    stdHeaders = []
    namespace = doc.DocRoot._baseNS


class TestPostfix:
    def inline(self):
        return "inline"

    def solo(self):
        return "solo"


class DummyBlog:
    postfix = None


class uPost(libpry.AutoTree):
    def setUp(self):
        self.post = self.getPost()
        self.post.postfix = TestPostfix()

    def test_repr(self):
        repr(self.post)

    def getPost(self):
        return blog.Post("blogpages/testpost", DummyBlog())

    def test_cmp(self):
        p = self.getPost()
        p2 = self.getPost()
        assert p != p2

    def test_fromStr(self):
        def check(title, time, data, short):
            assert title == "my title"
            assert time == datetime.datetime(1977, 11, 24, 14, 05)
            d = data.strip()
            assert d.startswith("this")
            assert d.endswith("data")
            d = short.strip()
            assert d.startswith("this is the")
            assert d.endswith("this post")

        data = """
            my title
            short: this is the 
            short description
            of this post
            time: 1977-11-24 14:05

            this
            is
            data
        """
        title, time, data, short = blog.Post.fromStr(data)
        check(title, time, data, short)

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
        check(title, time, data, short)

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
        p = blog.Post("blogpages/testpost_noshort", DummyBlog())
        title, time, data, short = blog.Post.fromStr(p.toStr())
        assert p.short == short
        assert p.title == title
        assert p.time == time
        assert p.data == data


class uRewriteTests(libpry.AutoTree):
    def setUp(self):
        self.bdir = os.path.join(self.tmpdir(), "blog")
        shutil.copytree("testblog", self.bdir)

    def test_rewrite(self):
        post = blog.Post(os.path.join(self.bdir, "posthree"), DummyBlog())
        assert post.changed
        post.rewrite()
        post = blog.Post(os.path.join(self.bdir, "posthree"), DummyBlog())
        assert not post.changed


class uBlogDirectory(libpry.AutoTree):
    def test_init(self):
        a = doc.Doc(
                TestRoot(
                    [
                        blog.BlogDirectory("testblog", None, DummyBlog())
                    ]
                )
            )
        #a.root.dump()


class uBlog(libpry.AutoTree):
    def setUp(self):
        self.b = blog.Blog(
                    "Blog Title",
                    "blog description",
                    "http://foo",
                    "posts",
                    "testblog",
                    blog.Disqus("test"),
                )
        r = TestRoot(
                    [
                        self.b(),
                        self.b.index("index.html", "Blog"),
                        self.b.archive("name.html", "Title"),
                        self.b.rss("rss.xml", "RS"),
                    ]
                )
        r.postfix = TestPostfix()
        self.a = doc.Doc(r)

    def tearDown(self):
        self.a._resetState()

    def test_invalid_blogdir(self):
        libpry.raises(
            "not a directory", blog.Blog,
            "Title", "description", "http://foo", "nonexistent", "nonexistent"
        )

    def test_render(self):
        self.a.render(self.tmpdir())

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
        p = self.b.index("name", "my title")
        countershape.state.application = self.a
        countershape.state.page = p
        assert p.name == "name"
        assert p.title == "my title"
        p._getIndex()

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
