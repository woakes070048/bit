# system
import logging
# flask_appbuilder
from flask_appbuilder import Model
# sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class Identify(Model):
    """Identify user model."""

    __tablename__ = 'bit_analytics_identify'  # sql table name

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))  # user id from source
    name = Column(String(255))  # user name
    email = Column(String(255))  # user email

    # def serialize(self):
    #     return {
    #         'id': self.id,
    #         'user_id': self.user_id,
    #         'name': self.name,
    #         'email': self.email,
    #     }
