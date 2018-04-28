import importlib
import re

__all__ = [
    'dynamic_import', 'verify_variable_type', 'verify_configuration',
    'matches', 'arg_to_iter', 'compile_regexes', 'unique_list'
]

RE_TYPE = type(re.compile('', 0))


def dynamic_import(full_name, *args):
    """
    Dynamic import a function or class based on the specified full name.

    Example:
        common_crawler.xxx.func -> common_crawler.xxx is the module name, func is the function name
        common_crawler.xxx.Hello -> common_crawler.xxx is the module name, Hello is the class name

    :param full_name: the full name of a function or class
    :param args: the args list for a function or a constructor in a class
    :return the return value of a function or instance object of a class
    :raise TypeError if the full name is wrong
    """
    verify_variable_type(full_name, str, 'The full name must be the string')

    last_spot = full_name.rfind('.')
    module = importlib.import_module(full_name[:last_spot])
    target = getattr(module, full_name[last_spot + 1:])

    if len(args) > 0:
        return target(*args)
    else:
        return target()


def verify_variable_type(var, expect_type, message):
    if not isinstance(var, expect_type):
        raise TypeError(message + ', got %s (type: %s)' % (var, var.__class__.__name__))


def verify_configuration(configuration):
    """
    Verify that the configuration file is valid.

    :param configuration: the configuration usually comes from configuration.py
    :return: if the configuration is illegal to return False otherwise to return True
    """
    return configuration is not None and isinstance(configuration, dict)


def matches(target, regexes):
    """
    Return the True if the target is matched success with regexes.

    :param regexes the list of the regex
    """
    return any(r.search(target) for r in regexes)


def arg_to_iter(arg):
    """
    Convert an argument to an iterable.
    """
    if arg is None:
        return []

    try:
        _ = (i for i in arg)
        return arg
    except TypeError:
        return [arg]


def compile_regexes(arg):
    """
    Compile the element as ReGex object if this element is not a ReGex object.
    """
    return [x if isinstance(x, RE_TYPE) else re.compile(x)
            for x in arg]


def unique_list(list_, key=lambda x: x):
    """Uniquify a list and preserving order"""
    result = []
    seen = set()
    for i in list_:
        seen_key = key(i)
        if seen_key in seen:
            continue
        seen.add(seen_key)
        result.append(i)
    return result
