"""Classes implementing the matcher pattern for testing"""
# pylint: disable=too-few-public-methods

import re


class Matcher:
    """
    An abstract class for the matcher testing pattern whereby an object
    stands in for another and will evaluate to true when compared with the
    other.
    """

    def __init__(self, description):
        self.description = description

    def __str__(self):
        return self.description

    def __repr__(self):
        return f"<{self.__class__.__name__} '{str(self)}'>"


class LambdaMatcher(Matcher):
    """
    Implements the matcher pattern when given a test function which tests if we
    are equal to another object.
    """

    def __init__(self, description, test_function):
        super().__init__(description)
        self.test_function = test_function

    def __eq__(self, other):
        return self.test_function(other)


class Anything(LambdaMatcher):
    """A class that matches anything"""

    def __init__(self):
        super().__init__("* anything *", lambda _: True)


class AnyFunction(LambdaMatcher):
    """A class that matches any callable object"""

    def __init__(self):
        super().__init__("* any callable *", callable)


class AnyString(LambdaMatcher):
    """A class that matches any string"""

    def __init__(self):
        super().__init__("* any string *", lambda other: isinstance(other, str))


class AnyStringContaining(LambdaMatcher):
    """A class that matches any string with a certain substring"""

    def __init__(self, sub_string):
        super().__init__(
            f"*{sub_string}*",
            lambda other: isinstance(other, str) and sub_string in other,
        )


class AnyStringMatching(LambdaMatcher):
    """A class that matches any regular expression"""

    def __init__(self, pattern, flags=0):
        """
        :param pattern: The raw pattern to compile into a regular expression
        :param flags: Flags `re` e.g. `re.IGNORECASE`
        """
        regex = re.compile(pattern, flags)
        super().__init__(
            pattern, lambda other: isinstance(other, str) and regex.match(other)
        )


class AnyInstanceOfClass(LambdaMatcher):
    """A class that matches any instance of another class"""

    def __init__(self, klass):
        super().__init__(klass.__name__, lambda other: isinstance(other, klass))
