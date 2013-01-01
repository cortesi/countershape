import urllib, UserDict, os, os.path, fnmatch
import cubictemp


def escape(s):
    if getattr(s, "_cubictemp_unescaped", 0):
        return unicode(s)
    else:
        return cubictemp.escape(unicode(s))


class InDir(object):
    def __init__(self, path):
        self.path = path
        self.oldpath = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, type, value, traceback):
        os.chdir(self.oldpath)


def makeURL(destination, **args):
    """
        If destination is a list-like object, it is treated as a series of path
        components.

        Creates a link with the given destination and page arguments. If the
        argument value is sequence-like (not string-like) it will be treated as
        mulitple values with the same name.
    """
    # FIXME: Examine the quoting situation here. Should we also CGI escape? Or
    # is urllib quoting enough?
    astr = []
    if args:
        for a in args:
            if isSequenceLike(args[a]):
                for i in args[a]:
                    astr.append(
                        "%s=%s"%(
                            urllib.quote(unicode(a), safe="{}"),
                            urllib.quote(unicode(i), safe="{}")
                        )
                    )
            else:
                k = urllib.quote(unicode(a), safe="{}")
                v = urllib.quote(unicode(args[a]), safe="{}")
                astr.append("%s=%s"%(k, v))
        astr = "?" + "&".join(astr)
    return "%s%s"%(destination, astr or "")


def urlCat(*urls):
    """
        Concatenate a series of URLs correctly.
    """
    out = []
    for i, s in enumerate(urls):
        if s:
            if i == 0:
                out.append(s.rstrip("/"))
            elif i == len(urls)-1:
                out.append(s.lstrip("/"))
            else:
                out.append(s.strip("/"))
    return "/".join(out)


def isStringLike(anobj):
    try:
        # Avoid succeeding expensively if anobj is large.
        anobj[:0]+''
    except:
        return False
    else:
        return True


def isSequenceLike(anobj):
    """
        Is anobj a non-string sequence type (list, tuple, iterator, or
        similar)?  Crude, but mostly effective.
    """
    if not hasattr(anobj, "next"):
        if isStringLike(anobj):
            return False
        try:
            anobj[:0]
        except:
            return False
    return True


def isNumeric(obj):
    try:
        obj + 0
    except:
        return False
    else:
        return True


fileExcludePatterns = ["*.svn*", "*/*.swp", "*/*.swo", "*/README"]

def walkTree(path, exclude=fileExcludePatterns):
    for root, dirs, files in os.walk(path):
        for f in files:
            relpath = os.path.join(root[len(path)+1:], f)
            for patt in exclude:
                if fnmatch.fnmatch(relpath, patt):
                    break
            else:
               yield relpath


class OrderedSet(list):
    """
        An implementation of a subset of the features of an ordered set. This
        object behaves, in general, like a list, but no item can be added to it
        twice. If an item already exists, attempts to add it will be ignored.

        The implementation is not complete - it should be extended if a wider
        subset of features is required.
    """
    def __init__(self):
        list.__init__(self)
        self.itmSet = set()

    def append(self, itm):
        if not itm in self.itmSet:
            self.itmSet.add(itm)
            return list.append(self, itm)

    def extend(self, itr):
        for i in itr:
            self.append(i)

    def insert(self, index, obj):
        if not obj in self.itmSet:
            self.itmSet.add(obj)
            return list.insert(self, index, obj)

    def __setitem__(self, index, obj):
        if not obj in self.itmSet:
            self.itmSet.add(obj)
            if len(self) >= index + 1:
                self.itmSet.remove(self[index])
            return list.__setitem__(self, index, obj)

    def __str__(self):
        try:
            l=[unicode(i) for i in self]
        except UnicodeDecodeError:
            l=[unicode(str(i),'latin-1','ignore') for i in self]
        return "\n".join(l)


class BuffIter:
    """
        An iterator with a pushback buffer.
    """
    def __init__(self, itr):
        self.buff = []
        self.itr = iter(itr)

    def push(self, itm):
        self.buff.append(itm)

    def __iter__(self):
        return self

    def next(self):
        if self.buff:
            return self.buff.pop()
        else:
            return self.itr.next()


class Data:
    def __init__(self, name):
        m = __import__(name)
        dirname, _ = os.path.split(m.__file__)
        self.dirname = os.path.abspath(dirname)

    def path(self, path):
        """
            Returns a path to the package data housed at 'path' under this
            module.Path can be a path to a file, or to a directory.

            This function will raise ValueError if the path does not exist.
        """
        fullpath = os.path.join(self.dirname, path)
        if not os.path.exists(fullpath):
            raise ValueError, "dataPath: %s does not exist."%fullpath
        return fullpath

data = Data(__name__)
