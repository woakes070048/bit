"""empty message

Revision ID: 539731d03773
Revises: 6c459f0bd819
Create Date: 2017-10-31 14:49:13.353000

"""

# revision identifiers, used by Alembic.
revision = '539731d03773'
down_revision = '6c459f0bd819'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_etl_tables', sa.Column('save_in_prt', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bit_etl_tables', 'save_in_prt')
    # ### end Alembic commands ###
