import importlib
import re

__all__ = [
    'dynamic_import', 'verify_variable_type', 'verify_configuration',
    'matches', 'arg_to_iter', 'compile_regexes', 'unique_list',
    'DynamicImportReturnType', 'get_function_by_name'
]

RE_TYPE = type(re.compile('', 0))


class DynamicImportReturnType(object):
    FUNCTION = 'FUNCTION',
    CLASS = 'CLASS',
    VARIABLE = 'VARIABLE'


def dynamic_import(full_name, return_type, *args, **kwargs):
    """
    Dynamic import a function or class and variable based on the specified full name.

    Example:
        common_crawler.xxx.func -> common_crawler.xxx is the module name, func is the function name
        common_crawler.xxx.Hello -> common_crawler.xxx is the module name, Hello is the class name

    :param full_name: the full name of a function or class and variable
    :param args: the args list for a function or a constructor in a class
    :param kwargs: the keyword arguments for a function or a constructor in a class
    :return the return value of a function or instance object of a class and variable
    :raise TypeError if the full name is wrong
    :raise AttributeError if the return_type is invalid
    """
    verify_variable_type(full_name, str, 'The full name must be the string')

    last_spot = full_name.rfind('.')
    module = importlib.import_module(full_name[:last_spot])
    target = getattr(module, full_name[last_spot + 1:])

    if return_type == DynamicImportReturnType.FUNCTION \
            or return_type == DynamicImportReturnType.CLASS:
        if len(args) > 0:
            return target(*args)
        elif len(kwargs) > 0:
            return target(**kwargs)
        else:
            return target()
    elif return_type == DynamicImportReturnType.VARIABLE:
        return target
    else:
        raise AttributeError('The param return_type is invalid, got %s' % return_type)


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
        # because str will not raise exception
        return arg if not isinstance(arg, str) else [arg]
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


def get_function_by_name(obj, func_names):
    func_names = arg_to_iter(func_names)
    for func_name in func_names:
        if hasattr(obj, func_name):
            return getattr(obj, func_name)
    return None
