"""empty message

Revision ID: 4ad33f99723a
Revises: 743a0a1b5bc9
Create Date: 2017-08-17 14:36:49.229000

"""

# revision identifiers, used by Alembic.
revision = '4ad33f99723a'
down_revision = '743a0a1b5bc9'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bit_facebook_daily_ad_insights_impression_device',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.String(length=255), nullable=True),
    sa.Column('campaign_id', sa.String(length=255), nullable=True),
    sa.Column('adset_id', sa.String(length=255), nullable=True),
    sa.Column('campaign_name', sa.String(length=255), nullable=True),
    sa.Column('spend', sa.Numeric(), nullable=True),
    sa.Column('cost_per_unique_click', sa.Numeric(), nullable=True),
    sa.Column('unique_clicks', sa.Integer(), nullable=True),
    sa.Column('unique_impressions', sa.Integer(), nullable=True),
    sa.Column('unique_social_clicks', sa.Integer(), nullable=True),
    sa.Column('unique_social_impressions', sa.Integer(), nullable=True),
    sa.Column('website_clicks', sa.Integer(), nullable=True),
    sa.Column('date_start', sa.DateTime(), nullable=True),
    sa.Column('date_stop', sa.DateTime(), nullable=True),
    sa.Column('impression_device', sa.String(length=255), nullable=True),
    sa.Column('ad_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ad_id'], ['bit_facebook_ad.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bit_facebook_daily_ad_insights_impression_device_impression_device'), 'bit_facebook_daily_ad_insights_impression_device', ['impression_device'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bit_facebook_daily_ad_insights_impression_device_impression_device'), table_name='bit_facebook_daily_ad_insights_impression_device')
    op.drop_table('bit_facebook_daily_ad_insights_impression_device')
    # ### end Alembic commands ###
