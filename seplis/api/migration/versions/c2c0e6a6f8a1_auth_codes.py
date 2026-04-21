"""auth codes

Revision ID: c2c0e6a6f8a1
Revises: ba4acf634b4d
Create Date: 2026-04-20 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c2c0e6a6f8a1'
down_revision = 'ba4acf634b4d'


def upgrade() -> None:
    op.create_table(
        'auth_codes',
        sa.Column('code', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('scopes', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('code'),
    )
    op.create_index(
        op.f('ix_auth_codes_expires_at'),
        'auth_codes',
        ['expires_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_auth_codes_user_id'),
        'auth_codes',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_auth_codes_user_id'), table_name='auth_codes')
    op.drop_index(op.f('ix_auth_codes_expires_at'), table_name='auth_codes')
    op.drop_table('auth_codes')
