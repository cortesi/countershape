import countershape.doc

ns.data = readFrom("_notcopied.html")

pages = [
    countershape.doc.Page("test.html", "Test"),
    countershape.doc.Directory("foo")
]
