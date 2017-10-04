# flask_appbuilder
from flask_appbuilder import Model

# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# superset
from sqlalchemy_utils import generic_relationship
from superset import sm


class Connector(Model):
    """Global BIT Connector."""

    __tablename__ = 'bit_connectors'  # sql table name

    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # connector name
    type = Column(String(255))  # type connector

    # object = generic_relationship(type, id)

    user_id = Column(Integer, ForeignKey('ab_user.id'))
    owner = relationship(
        sm.user_model,
        backref='connectors',
        foreign_keys=[user_id]
    )

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'connector'
    }

    def __repr__(self):
        """Object name."""
        return '{} [{}]'.format(self.type, self.name)

    def get_list_data_sources(self):
        """Return All Data Sources for connector"""
        raise NotImplementedError()

    def admin_data_sources(self):
        """Return All Data Sources for connector"""
        raise NotImplementedError()

    def get_columns(self):
        """Return All Data Sources Column for connector"""
        raise NotImplementedError()

    def get_data(self):
        """Return All Data Sources data for connector"""
        raise NotImplementedError()

