"""empty message

Revision ID: c10accd915ce
Revises: 734a03a63039
Create Date: 2017-08-14 14:13:48.688000

"""

# revision identifiers, used by Alembic.
revision = 'c10accd915ce'
down_revision = '734a03a63039'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_facebook_daily_ad_insights', sa.Column('date_stop', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bit_facebook_daily_ad_insights', 'date_stop')
    # ### end Alembic commands ###
