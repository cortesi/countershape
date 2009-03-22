import libpry
import countershape.textish as tx


class u_HTML(libpry.AutoTree):
    def test_str(self):
        h = tx._HTML("foo"*10)
        str(h)
        repr(h)


class u_ExtractHTML(libpry.AutoTree):
    def test_init(self):
        s = """<span></span>
            pre<div>
                pre<div>inside</div>post
                inside
            </div>post
        
            a paragraph

            pre<div>inside</div>post
        """
        x = tx._ExtractHTML(s)
        b = x.getBlocks()
        assert len(b) == 11
        assert str(b[-1]).strip() == "post"

        s = "foo"
        x = tx._ExtractHTML(s)
        b = x.getBlocks()
        assert b == [tx._Terminal(), tx._Text("foo")]

    def test_htmlspace(self):
        s = "one <span></span> two"
        x = tx._ExtractHTML(s)
        b = x.getBlocks()
        assert len(b) == 4

    def test_htmlnewline(self):
        s = "one <span></span>\ntwo"
        x = tx._ExtractHTML(s)
        b = x.getBlocks()
        assert len(b) == 4

    def test_getBlocks_empty(self):
        x = tx._ExtractHTML("")
        assert x.getBlocks() == [tx._Terminal()]

    def test_splitText(self):
        x = tx._ExtractHTML("")
        s = "onetwo\n\nthree"
        assert len(x._splitText(s)) == 3

        s = "onetwo\n\nthree\n\n"
        assert len(x._splitText(s)) == 4

        s = "\n\nonetwo\n\nthree\n\n"
        assert len(x._splitText(s)) == 5

    def test_getData(self):
        x = tx._ExtractHTML("")
        data = [
            "one",
            "two",
            "three"
        ]
        assert x._getData(data, 1, 0, 1, 2) == "on"
        assert x._getData(data, 1, 0, 2, 2) == "onetw"

    def test_regexps(self):
        l = "foo\n\nbar\n\nbar"
        assert len(tx._ExtractHTML._splitRe.split(l)) == 7

        l = "\n\nfoo\n\nbar\n\nbar\n\n"
        assert len(tx._ExtractHTML._splitRe.split(l)) == 13


class uLists(libpry.AutoTree):
    def test_list(self):
        s = "<p></p>\n\n:foo bar\n:foo voing"
        self.t = tx.Textish(s)
        assert self.t.count() == 11 


class uTextish(libpry.AutoTree):
    def setUp(self):
        self.t = tx.Textish("")
        self.t.clear()

    def test_repr(self):
        repr(self.t)

    def test_defRe(self):
        assert tx._Text._isDefRe.match("   \t\t\t:foo")
        assert tx._Text._isDefRe.match("   \t\t\t:__foo__")
        assert not tx._Text._isDefRe.match("   \t\t\t: foo")

        l = tx._Text._splitDefRe.finditer("   \t\t:foo foo bar")
        assert len(list(l)) == 1

        l = tx._Text._splitDefRe.finditer("""
                :foo asdfasdf asdfasfd
                :bar foo bar
            """)
        assert len(list(l)) == 2

    def test_listRes(self):
        assert tx._Text._isLiRe.match("   \t\t\t* foo")
        assert tx._Text._isLiRe.match("* foo")
        assert not tx._Text._isLiRe.match("   \t\tfoo")

        l = tx._Text._splitLiRe.split("   \t\t\* foo")
        assert len(l) == 1

        l = tx._Text._splitLiRe.split("* foo\n* bar")
        assert len(l) == 3

    def test_splitListItems(self):
        self.t.addChildrenFromList(
            [tx._Terminal(), tx._Text("* one\n* two <a href=\'foo\'>foo</a> bar\n* three")]
        )
        self.t._call("_splitListItems")
        assert self.t.count() == 8

        self.t.clear()
        self.t.addChildrenFromList(
            [tx._Terminal(), tx._Text("* one\n")]
        )
        self.t._call("_splitListItems")
        assert self.t.count() == 4
        assert self.t.children[1].children[0].s.strip() == "one"

        self.t.clear()
        self.t.addChildrenFromList(
            [
                tx._Terminal(),
                tx._Text("* one\n"),
                tx._Terminal(),
                tx._Text("* two\n"),
            ]
        )
        self.t._call("_splitListItems")
        assert self.t.count() == 7
        assert self.t.children[1].children[0].s.strip() == "one"

    def test_collectLists(self):
        self.t.addChildrenFromList(
            [
                tx._ListItem([tx._Text("one")]),
                tx._ListItem([tx._Text("two")]),
                tx._ListItem([tx._Text("three")]),
            ]
        )
        self.t._collectLists()
        assert self.t.count() == 8
        assert len(self.t.children[0].children) == 3
        assert self.t.children[0].count() == 7

        self.t.clear()
        self.t.addChildrenFromList(
            [
                tx._Text("text"),
                tx._ListItem([tx._Text("one")]),
                tx._ListItem([tx._Text("two")]),
                tx._ListItem([tx._Text("three")]),
                tx._Terminal(),
                tx._Text("text"),
            ]
        )
        self.t._collectLists()
        assert len(self.t.children) == 3
        assert self.t.count() == 13

    def test_collectLists_term(self):
        self.t.addChildrenFromList(
            [
                tx._Text("text"),
                tx._ListItem(
                    [tx._Text("one")]
                ),
                tx._Terminal(),
                tx._ListItem(
                    [tx._Text("two")]
                ),
                tx._Terminal(),
                tx._ListItem(
                    [tx._Text("three")]
                ),
                tx._Terminal(),
                tx._Text(
                    ("text")
                ),
            ]
        )
        self.t._collectLists()
        assert len(self.t.children) == 3
        assert self.t.count() == 13

    def test_headingRe(self):
        assert tx._Text._headingRe.match("foo\n--")
        assert tx._Text._headingRe.match(":::foo\n--")
        assert tx._Text._headingRe.match("   \t\t\t foo\n--")
        assert not tx._Text._headingRe.match("   \t\t\t foo\n")
        assert not tx._Text._headingRe.match("foo\n\n---")

        m = tx._Text._headingRe.match("   \t\t\t foo\n--")
        assert m.group("text") == "foo"
        assert m.group("type") == "--"
        assert not m.group("depth")

        m = tx._Text._headingRe.match(":::foo\n===")
        assert m.group("text") == "foo"
        assert m.group("type") == "==="
        assert m.group("depth") == ":::"

    def test_markupRe(self):
        assert len(tx._Text._markupRe.split("one two three")) == 1
        assert len(tx._Text._markupRe.split("one _two_ three")) == 3
        assert len(tx._Text._markupRe.split("one _two three_ four")) == 3
        assert len(tx._Text._markupRe.split("one _two three four")) == 1
        assert len(tx._Text._markupRe.split("one _two_ __three__ four")) == 5
        assert len(tx._Text._markupRe.split("one _t\nw\no_ three")) == 3

    def test_footnoteRe(self):
        assert len(tx._Text._footnoteRe.split("one two three")) == 1

    def test_makeHeadings(self):
        self.t.addChildrenFromList(
            [
                tx._Text("one\n--"),
                tx._Text("::two\n--"),
                tx._Text("three\n=="),
                tx._Text("::four\n=="),
                tx._Text("plain"),
            ]
        )
        self.t._call("_makeHeadings", 0)
        assert self.t.children[0].s == "one"
        assert self.t.children[0].depth == 2

        assert self.t.children[1].s == "two"
        assert self.t.children[1].depth == 2

        assert self.t.children[2].s == "three"
        assert self.t.children[2].depth == 1

        assert self.t.children[3].s == "four"
        assert self.t.children[3].depth == 2

        assert self.t.children[4].s == "plain"

    def test_makeParagraphs(self):
        self.t.addChildrenFromList(
            [
                tx._Text("one\n--"),
                tx._HTML("<foo></foo>"),
                tx._HTML("<foo></foo>"),
                tx._Text("three\n=="),
                tx._Terminal(),
                tx._Text("one\n--"),
            ]
        )
        self.t._call("_makeParagraphs")
        assert len(self.t.children) == 3
        assert self.t.children[0].count() == 5

    def test_makeParagraphs_htmlInitial(self):
        self.t.addChildrenFromList(
            [
                tx._HTML("<foo></foo>"),
                tx._Text("one\n--"),
                tx._Text("three\n=="),
                tx._Terminal(),
            ]
        )
        self.t._call("_makeParagraphs")
        assert len(self.t.children) == 3
        assert isinstance(self.t.children[1], tx._Paragraph)

    def test_makeMarkup(self):
        self.t.addChildrenFromList(
            [
                tx._Text("one _two_ __three__ four"),
            ]
        )
        self.t._call("_makeMarkup")
        assert self.t.count() == 8
        

class u_Terminal(libpry.AutoTree):
    def test_str(self):
        s = tx._Terminal()
        str(s)
        repr(s)


class u_Wrap(libpry.AutoTree):
    def test_str(self):
        s = tx._Strong(
                [
                    tx._Text("fo"),
                    tx._Text("o")
                ]
            )
        assert str(s) == "<strong>foo</strong>"
        assert repr(s)


class u_Heading(libpry.AutoTree):
    def test_str(self):
        s = tx._Heading(1, "foo")
        assert str(s) == "<h1>foo</h1>"
        repr(s)

    def test_full(self):
        s = """
            Foo
            ===
        """
        t = tx.Textish(s)
        assert t.count() == 3


class uTextish_EndToEnd(libpry.AutoTree):
    def countTypes(self, t, klass):
        return len([i for i in t.preOrder() if isinstance(i, klass)])

    def test_paragraphs(self):
        s = """
            this is a paragraph <a href="">containing</a> <a href="">links</a> and more text.
        """
        t = tx.Textish(s)
        assert len(t.children) == 2
        assert len(t.children[1].children) == 5

    def test_deflist(self):
        s = """
            :foo This is foo's definition. 
            :bar This is bar's definition, spanning
            multiple lines.
        """
        t = tx.Textish(s)
        assert len(t.children) == 2
        assert len(t.children[1].children) == 4

    def test_full(self):
        s = """
            H1
            ==

            This is a paragraph <div> with a 
                
                contained

                div
            </div> * this is not a list item
            * neither is this

            * But this _is_ a list item
            * And this is a _list_  item containing <a href="foo">a link</a>

            * And this is a list item

            Another __paragraph__ 

            * Another List
            * Another List
            
            This is a definition list:

            :foo This is foo's definition. 
            :bar This is bar's definition, spanning
            multiple lines.

            Some text.


            :foo A single definition
        """
        t = tx.Textish(s)
        #t.dump()
        assert self.countTypes(t, tx._ListItem) == 5
        assert self.countTypes(t, tx._List) == 2
        str(t)


tests = [
    u_HTML(),
    u_ExtractHTML(),
    uTextish(),
    uLists(),
    u_Terminal(),
    u_Wrap(),
    u_Heading(),
    uTextish_EndToEnd()
]
