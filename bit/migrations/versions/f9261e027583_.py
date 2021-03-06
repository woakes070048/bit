"""empty message

Revision ID: f9261e027583
Revises: c0d2834887cd
Create Date: 2017-08-14 15:09:15.114000

"""

# revision identifiers, used by Alembic.
revision = 'f9261e027583'
down_revision = 'c0d2834887cd'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_facebook_daily_ad_insights', sa.Column('date_start', sa.DateTime(), nullable=True))
    op.drop_index('ix_bit_facebook_daily_ad_insights_native_id', table_name='bit_facebook_daily_ad_insights')
    op.drop_column('bit_facebook_daily_ad_insights', 'native_id')
    op.drop_column('bit_facebook_daily_ad_insights', 'campaign_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_facebook_daily_ad_insights', sa.Column('campaign_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('bit_facebook_daily_ad_insights', sa.Column('native_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_index('ix_bit_facebook_daily_ad_insights_native_id', 'bit_facebook_daily_ad_insights', ['native_id'], unique=True)
    op.drop_column('bit_facebook_daily_ad_insights', 'date_start')
    # ### end Alembic commands ###
