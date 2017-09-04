"""empty message

Revision ID: 538751338a0f
Revises: fd235fe43a42
Create Date: 2017-08-07 14:43:12.256000

"""

# revision identifiers, used by Alembic.
revision = '538751338a0f'
down_revision = 'fd235fe43a42'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bit_etl_tables', sa.Column('sync_last_time', sa.DateTime(), nullable=True))
    op.add_column('bit_etl_tables', sa.Column('sync_next_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bit_etl_tables', 'sync_next_time')
    op.drop_column('bit_etl_tables', 'sync_last_time')
    # ### end Alembic commands ###
