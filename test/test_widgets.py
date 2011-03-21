import countershape
from countershape.widgets import *
import testpages

class uPageIndex(testpages.DummyState):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot(
                [
                    testpages.TPageHTML("one"), [
                        testpages.TPageHTML("one-one"),
                        testpages.TPageHTML("one-two"),
                        testpages.TPageHTML("one-three"),[
                            testpages.TPageHTML("one-three-one"),
                        ]
                    ],
                    testpages.TPage("marker"),
                    testpages.TPage("two", internal=True, structural=True),
                    testpages.TPageHTML("three"),
                    testpages.TPageHTML("exclude"),[
                        testpages.TPageHTML("exclude2"),
                    ],
                    testpages.TPageHTML("nest1"),[
                        testpages.TPageHTML("nest2"),
                    ]
                ]
            )
        )
        self.pageName = "one"
        testpages.DummyState.setUp(self)

    def test_render(self):
        p = str(SiblingPageIndex("one", 2, exclude=["exclude"]))
        assert "one-one" in p
        assert "three" in p
        assert not "one-three-one" in p
        assert "<a>two" in p
        assert "exclude" not in p

    def test_render_extendededparentpageindex(self):
        p = str(ExtendedParentPageIndex("one", 2, exclude=["exclude"]))
        assert "one-one" in p

    def test_nosib(self):
        p = str(SiblingPageIndex())
        assert "one-one" in p
        assert "three" in p

    def test_parent(self):
        p = str(ParentPageIndex("one"))
        assert "one-one" in p
        assert not "marker" in p

    def test_parentnesting(self):
        p = str(ParentPageIndex("nest1"))
        assert "nest1" in p
        assert "nest2" in p

    def test_currentactive(self):
        str(ParentPageIndex("nest1", currentActive=True))


class CSiblingNavBarPage(testpages.TPageHTML):
    def body(self):
        yield SiblingNavBar(self, _class="myclass")()


class CNonstructuralPage(testpages.TPageHTML):
    structural = False
    def body(self):
        yield "Test."


class CNavBarPage(testpages.TPageHTML):
    def body(self):
        yield NavBar(["one", "two"], _class="myclass")


class uNavBar(testpages.RenderTester):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot([
                CSiblingNavBarPage("top"), [
                    CSiblingNavBarPage("one"), [
                        CSiblingNavBarPage("onechild"),
                    ],
                    CSiblingNavBarPage("two"),
                    CSiblingNavBarPage("three"),
                    CNonstructuralPage("nonstruct")
                ],
                CNavBarPage("fixedmenu")
            ])
        )

    def test_siblingNavBar(self):
        assert self.call("one")
        assert self.call("onechild")

    def test_menu(self):
        assert self.call("fixedmenu")


class uPageTrail(testpages.DummyState):
    def setUp(self):
        self.application = testpages.TestApplication(
            model.BaseRoot(
                [
                    testpages.TPage("one", internal=True, structural=True), [
                        testpages.TPageHTML("one-one"),
                    ]
                ]
            )
        )
        self.pageName = "one-one"
        testpages.DummyState.setUp(self)

    def test_init(self):
        s = PageTrail(state.page)
        str(s)



tests = [
    uPageIndex(),
    uNavBar(),
    uPageTrail(),
]
