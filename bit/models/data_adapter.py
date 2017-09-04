from decimal import Decimal
from dateutil import parser as dateutil_parser
from babel.numbers import parse_decimal

# superset
from superset import db

class DataAdapter(object):

    model = None

    def __init__(self, data):
        self.data = data

    def adapt(self):
        raise NotImplementedError()

    @classmethod
    def string_to_int(cls, value):
        if value is None:
            return None
        if not len(value):
            return 0
        return int(value)

    @classmethod
    def string_to_float(cls, value):
        if value is None:
            return None
        if not len(value):
            return 0.0
        return float(value)

    @classmethod
    def string_to_date(cls, value):
        if value is None:
            return None
        return dateutil_parser.parse(value).date()

    @classmethod
    def string_to_decimal(cls, value):
        if value is None:
            return None

        if not len(value):
            return Decimal.from_float(0.0)

        try:
            return parse_decimal(value)
        except Exception:
            return Decimal.from_float(0.0)

    @classmethod
    def bulk_adapt(cls, data_list):
        def items():
            for data in data_list:
                yield cls(data=data).adapt()

        for item in items():
            db.session.add(item)
        db.session.commit()

        ## cls.model.insert().values(items())
        # db.session.query(cls.model).insert().values(items())

        # cls.model.objects.bulk_create(objs=items()) Django

