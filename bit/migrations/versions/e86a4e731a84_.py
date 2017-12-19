"""empty message

Revision ID: e86a4e731a84
Revises: 9a85e02050e0
Create Date: 2017-12-19 12:25:41.564000

"""

# revision identifiers, used by Alembic.
revision = 'e86a4e731a84'
down_revision = '9a85e02050e0'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('table_columns', sa.Column('is_index', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('table_columns', 'is_index')
    # ### end Alembic commands ###
