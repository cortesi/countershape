import sys
import blog

def blog_tags(d, fp=sys.stdout):
    b = blog.find_blog(d)
    histogram = dict()
    for i in b.blogdir.sortedPosts():
        for t in i.tags:
            histogram[t] = histogram.get(t, 0) + 1
    vals = [(v, k) for (k, v) in histogram.items()]
    vals.sort(reverse=True)
    for i in vals:
        print >> fp, "%5i"%i[0], i[1]




