"""empty message

Revision ID: ae390b7a8ce7
Revises: 
Create Date: 2018-01-31 11:52:59.618812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae390b7a8ce7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('principal',
    sa.Column('login', sa.String(64), nullable=False),
    sa.Column('password_hash', sa.String(256), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('login')
    )


def downgrade():
    op.drop_table('principal')
