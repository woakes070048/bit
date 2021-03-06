"""empty message

Revision ID: 7b084e67d65d
Revises: 360caaea22f0
Create Date: 2017-08-23 16:39:40.757000

"""

# revision identifiers, used by Alembic.
revision = '7b084e67d65d'
down_revision = '360caaea22f0'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bit_chiter_connector',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('app_id', sa.String(length=255), nullable=True),
    sa.Column('api_token', sa.String(length=255), nullable=True),
    sa.Column('url_pat', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bit_chiter_connector')
    # ### end Alembic commands ###
