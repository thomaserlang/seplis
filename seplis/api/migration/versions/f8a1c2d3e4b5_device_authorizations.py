"""device authorizations

Revision ID: f8a1c2d3e4b5
Revises: c2c0e6a6f8a1
Create Date: 2026-09-26 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = 'f8a1c2d3e4b5'
down_revision = 'c2c0e6a6f8a1'


def upgrade() -> None:
    op.drop_index(op.f('ix_auth_codes_user_id'), table_name='auth_codes')
    op.drop_index(op.f('ix_auth_codes_expires_at'), table_name='auth_codes')
    op.drop_table('auth_codes')

    op.create_table(
        'device_authorizations',
        sa.Column('device_code_hash', sa.String(length=64), nullable=False),
        sa.Column('user_code', sa.String(length=6), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('scopes', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='cascade'),
        sa.PrimaryKeyConstraint('device_code_hash'),
    )
    op.create_index(
        op.f('ix_device_authorizations_expires_at'),
        'device_authorizations',
        ['expires_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_device_authorizations_user_code'),
        'device_authorizations',
        ['user_code'],
        unique=True,
    )
    op.create_index(
        op.f('ix_device_authorizations_user_id'),
        'device_authorizations',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_device_authorizations_user_id'),
        table_name='device_authorizations',
    )
    op.drop_index(
        op.f('ix_device_authorizations_user_code'),
        table_name='device_authorizations',
    )
    op.drop_index(
        op.f('ix_device_authorizations_expires_at'),
        table_name='device_authorizations',
    )
    op.drop_table('device_authorizations')

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
