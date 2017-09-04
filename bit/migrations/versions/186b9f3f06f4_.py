"""empty message

Revision ID: 186b9f3f06f4
Revises: 6e190685693b
Create Date: 2017-08-22 12:45:57.458000

"""

# revision identifiers, used by Alembic.
revision = '186b9f3f06f4'
down_revision = '6e190685693b'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_facebook_daily_ad_insights_impression_device', sa.Column('cost_per_mobile_app_installs', sa.Numeric(), nullable=True))
    op.add_column('bit_facebook_daily_ad_insights_impression_device', sa.Column('cost_per_mobile_app_purchases', sa.Numeric(), nullable=True))
    op.add_column('bit_facebook_daily_ad_insights_impression_device', sa.Column('mobile_app_installs', sa.Integer(), nullable=True))
    op.add_column('bit_facebook_daily_ad_insights_impression_device', sa.Column('mobile_app_purchases', sa.Integer(), nullable=True))
    op.add_column('bit_performance_report', sa.Column('cost_per_mobile_app_installs', sa.Numeric(), nullable=True))
    op.add_column('bit_performance_report', sa.Column('cost_per_mobile_app_purchases', sa.Numeric(), nullable=True))
    op.add_column('bit_performance_report', sa.Column('mobile_app_installs', sa.Integer(), nullable=True))
    op.add_column('bit_performance_report', sa.Column('mobile_app_purchases', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bit_performance_report', 'mobile_app_purchases')
    op.drop_column('bit_performance_report', 'mobile_app_installs')
    op.drop_column('bit_performance_report', 'cost_per_mobile_app_purchases')
    op.drop_column('bit_performance_report', 'cost_per_mobile_app_installs')
    op.drop_column('bit_facebook_daily_ad_insights_impression_device', 'mobile_app_purchases')
    op.drop_column('bit_facebook_daily_ad_insights_impression_device', 'mobile_app_installs')
    op.drop_column('bit_facebook_daily_ad_insights_impression_device', 'cost_per_mobile_app_purchases')
    op.drop_column('bit_facebook_daily_ad_insights_impression_device', 'cost_per_mobile_app_installs')
    # ### end Alembic commands ###