from bit.utils import parsers


sqla_python_types = {
     'String': str,
     'Text': str,
     'Integer': parsers.numparser(),
     'Numeric': parsers.numparser(),
     'Boolean': parsers.boolparser(),
     'DateTime': parsers.datetimeparser(),
 }
