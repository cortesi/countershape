from countershape import doc, sitemap

ns.data = readFrom("_notcopied.html")
this.site_url = "http://foo.com"

pages = [
    doc.Page("test.html", "Test"),
    doc.Directory("foo"),
    sitemap.Sitemap("sitemap.xml")
]
