# system
import six

# superset
from superset import db


class ModelHelper(object):
    """Model Helper."""

    @classmethod
    def update_or_create(cls, defaults=None, remove_id=False, **kwargs):
        """
        Looks up an object with the given kwargs, updating one with defaults
        if it exists, otherwise creates a new one.
        Returns a tuple (object, created), where created is a boolean
        specifying whether an object was created.
        """

        """
        obj, created = cls.update_or_create(
            connector=connector,
            account_id='517113408474457',
            defaults={'name': 'Bob'}
        )
        """

        # created = False
        defaults = defaults or {}

        if remove_id and 'id' in defaults:
            defaults.pop('id')

        # obj = db.session.query(cls).filter_by(**kwargs).first()
        #
        # if not obj:
        obj = cls(**kwargs)
        created = True

        for k, v in six.iteritems(defaults):
            setattr(obj, k, v)

        db.session.merge(obj)
        db.session.commit()

        return obj, created
