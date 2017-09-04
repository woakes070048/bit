"""empty message

Revision ID: 15e82138e107
Revises: d104dafc402b
Create Date: 2017-08-08 13:40:36.050000

"""

# revision identifiers, used by Alembic.
revision = '15e82138e107'
down_revision = 'd104dafc402b'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_etl_tables', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bit_etl_tables', 'is_active')
    # ### end Alembic commands ###