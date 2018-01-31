"""empty message

Revision ID: 1116ea193980
Revises: ae390b7a8ce7
Create Date: 2018-01-31 12:55:54.267103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1116ea193980'
down_revision = 'ae390b7a8ce7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('auth_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=128), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('expiry', sa.DateTime(), nullable=False),
    sa.Column('principal_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['principal_id'], ['principal.login'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('auth_token')
