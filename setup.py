import os
import platform
import sys
from distutils.core import setup


def _fnmatch(name, patternList):
    for i in patternList:
        if fnmatch.fnmatch(name, i):
            return True
    return False


def _splitAll(path):
    parts = []
    h = path
    while 1:
        if not h:
            break
        h, t = os.path.split(h)
        parts.append(t)
    parts.reverse()
    return parts


def findPackages(path, dataExclude=[]):
    """
        Recursively find all packages and data directories rooted at path. Note
        that only data _directories_ and their contents are returned -
        non-Python files at module scope are not, and should be manually
        included.

        dataExclude is a list of fnmatch-compatible expressions for files and
        directories that should not be included in pakcage_data.

        Returns a (packages, package_data) tuple, ready to be passed to the
        corresponding distutils.core.setup arguments.
    """
    packages = []
    datadirs = []
    for root, dirs, files in os.walk(path, topdown=True):
        if "__init__.py" in files:
            p = _splitAll(root)
            packages.append(".".join(p))
        else:
            dirs[:] = []
            if packages:
                datadirs.append(root)

    # Now we recurse into the data directories
    package_data = {}
    for i in datadirs:
        if not _fnmatch(i, dataExclude):
            parts = _splitAll(i)
            module = ".".join(parts[:-1])
            acc = package_data.get(module, [])
            for root, dirs, files in os.walk(i, topdown=True):
                sub = os.path.join(*_splitAll(root)[1:])
                if not _fnmatch(sub, dataExclude):
                    for fname in files:
                        path = os.path.join(sub, fname)
                        if not _fnmatch(path, dataExclude):
                            acc.append(path)
                else:
                    dirs[:] = []
            package_data[module] = acc
    return packages, package_data


packages, package_data = findPackages("countershape")
setup(
    name = "countershape",
    version = "0.2",
    description = "A framework for rendering static documentation.",
    author = "Nullcube Pty Ltd",
    author_email = "aldo@nullcube.com",
    url = "http://dev.nullcube.com",
    packages = packages,
    package_data = package_data,
    entry_points = {
        "console_scripts": [
            "cshape = countershape.cmdline:main"
        ]
    },
    install_requires=[
        "tinytree",
        "cubictemp",
        "docutils",
        "markdown2",
        "pygments",
        "livereload"
    ],
)
