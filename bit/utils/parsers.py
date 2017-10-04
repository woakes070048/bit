from dateutil import parser as dateutil_parser


def datetimeparser():

    def parser(value):
        return dateutil_parser.parse(value)

    return parser


def boolparser(true_strings=('true', 't', 'yes', 'y', '1'),
               false_strings=('false', 'f', 'no', 'n', '0'),
               case_sensitive=False,
               strict=True):
    """Return a function to parse strings as :class:`bool` objects using a
    given set of string representations for `True` and `False`. E.g.::

        >>> mybool = boolparser(
        >>>     true_strings=['yes', 'y'], false_strings=['no', 'n']
        >>> )
        >>> mybool('y')
        True
        >>> mybool('yes')
        True
        >>> mybool('Y')
        True
        >>> mybool('No')
        False
        >>> try:
        ...     mybool('foo')
        ... except ValueError as e:
        ...     print(e)
        ...
        value is not one of recognised boolean strings: 'foo'
        >>> try:
        ...     mybool('True')
        ... except ValueError as e:
        ...     print(e)
        ...
        value is not one of recognised boolean strings: 'true'

    If ``strict=False`` then if an error occurs when parsing, the original
    value will be returned as-is, and no error will be raised.

    """

    if not case_sensitive:
        true_strings = [s.lower() for s in true_strings]
        false_strings = [s.lower() for s in false_strings]

    def parser(value):
        value = value.strip()
        if not case_sensitive:
            value = value.lower()
        if value in true_strings:
            return True
        elif value in false_strings:
            return False
        elif strict:
            raise ValueError('value is not one of recognised boolean strings: '
                             '%r' % value)
        else:
            print(value)
            if value == '' or value == 'None':
                value = False
            return value

    return parser


def numparser(strict=False):
    """Return a function that will attempt to parse the value as a number,
    trying :func:`int`, :func:`long`, :func:`float` and :func:`complex` in
    that order. If all fail, return the value as-is, unless ``strict=True``,
    in which case raise the underlying exception.

    """

    def f(v):
        try:
            return int(v)
        except (ValueError, TypeError):
            pass
        try:
            return long(v)
        except (ValueError, TypeError):
            pass
        try:
            return float(v)
        except (ValueError, TypeError):
            pass
        try:
            return complex(v)
        except (ValueError, TypeError) as e:
            if strict:
                raise e
        if not v:
            v = 0
        if v == '' or v == 'None' or v == 'N/A':
            v = 0

        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

        return v

    return f

