import sys, os
import blog

def nicepath(b):
    cwdl = len(os.getcwd())
    return "." + b.src[cwdl:]

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


def blog_notags(d, fp=sys.stdout):
    b = blog.find_blog(d)
    for i in b.blogdir.sortedPosts():
        if not i.tags:
            print >> fp, nicepath(i)


def blog_has_option(d, option, fp=sys.stdout):
    cwdl = len(os.getcwd())
    b = blog.find_blog(d)
    for i in b.blogdir.sortedPosts():
        if option in i.options:
            print >> fp, nicepath(i)


def blog_has_no_option(d, option, fp=sys.stdout):
    cwdl = len(os.getcwd())
    b = blog.find_blog(d)
    for i in b.blogdir.sortedPosts():
        if option not in i.options:
            print >> fp, nicepath(i)


