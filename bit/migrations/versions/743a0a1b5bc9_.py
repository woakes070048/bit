"""empty message

Revision ID: 743a0a1b5bc9
Revises: f9261e027583
Create Date: 2017-08-17 13:33:46.055000

"""

# revision identifiers, used by Alembic.
revision = '743a0a1b5bc9'
down_revision = 'f9261e027583'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bit_facebook_daily_ad_insights')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bit_facebook_daily_ad_insights',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('ad_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('buying_type', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('unique_clicks', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('age', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('gender', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('date_stop', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ad_id'], [u'bit_facebook_ad.id'], name=u'bit_facebook_daily_ad_insights_ad_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'bit_facebook_daily_ad_insights_pkey')
    )
    # ### end Alembic commands ###
