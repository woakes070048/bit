"""empty message

Revision ID: 7dd23472cc3d
Revises: 539731d03773
Create Date: 2017-11-29 18:12:15.322000

"""

# revision identifiers, used by Alembic.
revision = '7dd23472cc3d'
down_revision = '539731d03773'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bit_analytics_identify',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=255), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bit_analytics_identify')
    # ### end Alembic commands ###
