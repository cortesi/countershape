import platform, sys
from distutils.core import setup
from distextend import *

packages, package_data = findPackages("countershape")
setup(
        name = "countershape",
        version = "0.1",
        description = "A framework for rendering static documentation.",
        author = "Nullcube Pty Ltd",
        author_email = "aldo@nullcube.com",
        url = "http://dev.nullcube.com",
        packages = packages,
        package_data = package_data,
        scripts = ["cshape"],
)
