"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from inspect import currentframe



def funcname() -> str:
    """
    Return the current function name where code is running.

    :returns: Current function name where code is running.
    """

    frame = currentframe()

    assert frame is not None, (
        'Frame not present')

    caller = frame.f_back

    assert caller is not None, (
        'Caller not present')

    name = caller.f_code.co_name
    focals = caller.f_locals


    if 'self' in focals:

        parent = (
            focals['self']
            .__class__
            .__name__)

        return f'{parent}.{name}'

    elif 'cls' in focals:

        parent = (
            focals['cls']
            .__name__)

        return f'{parent}.{name}'


    return name
