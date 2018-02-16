"""empty message

Revision ID: 348b2d5170d9
Revises: 1116ea193980
Create Date: 2018-01-31 16:03:38.965466

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '348b2d5170d9'
down_revision = '1116ea193980'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_auth_token_token'), 'auth_token', ['token'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_auth_token_token'), table_name='auth_token')
