from countershape import doc, sitemap, layout
ns.data = readFrom("_notcopied.html")
this.site_url = "http://foo.com"
this.layout = layout.DefaultLayout

pages = [
    doc.Page("test.html", "Test"),
    doc.Directory("foo"),
    sitemap.Sitemap("sitemap.xml")
]
