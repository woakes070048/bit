"""empty message

Revision ID: 734a03a63039
Revises: fa6a90ecfed1
Create Date: 2017-08-14 13:36:56.966000

"""

# revision identifiers, used by Alembic.
revision = '734a03a63039'
down_revision = 'fa6a90ecfed1'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_facebook_daily_ad_insights', sa.Column('campaign_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bit_facebook_daily_ad_insights', 'campaign_id')
    # ### end Alembic commands ###
