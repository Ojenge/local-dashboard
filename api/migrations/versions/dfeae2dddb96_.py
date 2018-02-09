"""empty message

Revision ID: dfeae2dddb96
Revises: 348b2d5170d9
Create Date: 2018-02-09 11:31:08.795628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfeae2dddb96'
down_revision = '348b2d5170d9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('principal', sa.Column('password_changed', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('principal', 'password_changed')
