# This is not a module comment
"""
    This is a
    module docstring
"""

#grok:include

import itertools

def func(arg):
    # This is a comment
    """
        This is a
        method docstring
    """
    #grok:include
    x = 1
    x = 2
    return 0

# Multiline
# comment
global_variable = (func(func(10)) + 10, 12)

global_variable2 = (
    func(func(10)) + 10, 12
)

_hidden_variable = 10

def funcComment(arg): pass # Comment


if 0:
    def nested(arg):
        pass


class Parent:
    def __foo__(self):
        if 1:
            if 2:
                if 3:
                    pass


class Mork:
    def commenterr(self):
        # foo
        # bar
        pass


# variabledoc
# multiline
variable = None

class Short: pass

class _Hidden: pass

class _HiddenOverride:
    #grok:include
    pass

class Foo(Parent):
    # This is a comment
    #grok:include
    """
        This is a
        class docstring
    """
    # classvardoc
    # multiline
    classvar = None
    def __init__(self, one, two="two"):
        """
            :one An argument.
        """
        pass    
    def _hidden(self):
        pass
    def _hidden_override(self):
        #grok:include
        pass
    def excluded(self):
        #grok:exclude
        pass
    def meth(self, one, two=func(("one)", "two")), *args, **kwargs):
        """
            This is a
            method docstring
        """
        pass

    def meth2(self): pass

    @classmethod
    def cmeth(klass):
        if 0:
            if 0:
                if 0:
                    pass


class NoClassDoc(_InputField):
    def __str__(self):
        foo = bar
        voing = oink
