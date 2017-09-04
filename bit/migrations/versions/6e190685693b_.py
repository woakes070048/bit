"""empty message

Revision ID: 6e190685693b
Revises: 84ad5a52b596
Create Date: 2017-08-21 20:27:04.969000

"""

# revision identifiers, used by Alembic.
revision = '6e190685693b'
down_revision = '84ad5a52b596'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bit_adwords_campaign_performance_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('campaign_name', sa.String(length=255), nullable=True),
    sa.Column('cost', sa.Numeric(), nullable=True),
    sa.Column('clicks', sa.Integer(), nullable=True),
    sa.Column('impression_device', sa.String(length=255), nullable=True),
    sa.Column('impressions', sa.Integer(), nullable=True),
    sa.Column('conversions', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bit_adwords_campaign_performance_report_impression_device'), 'bit_adwords_campaign_performance_report', ['impression_device'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bit_adwords_campaign_performance_report_impression_device'), table_name='bit_adwords_campaign_performance_report')
    op.drop_table('bit_adwords_campaign_performance_report')
    # ### end Alembic commands ###
