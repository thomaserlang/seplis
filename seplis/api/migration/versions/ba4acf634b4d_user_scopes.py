"""User scopes

Revision ID: ba4acf634b4d
Revises: 80d7e0a4b3bf
Create Date: 2023-09-07 19:05:09.043880

"""

# revision identifiers, used by Alembic.
revision = 'ba4acf634b4d'
down_revision = '80d7e0a4b3bf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
        ALTER TABLE `tokens` 
        ADD COLUMN `id` BIGINT NOT NULL AUTO_INCREMENT AFTER `user_id`,
        DROP PRIMARY KEY,
        ADD PRIMARY KEY (`id`);
    ''')
    op.alter_column('tokens', 'token', type_=sa.String(2000), existing_type=sa.String(255))
    op.add_column('users', sa.Column('scopes', sa.String(2000), nullable=False, server_default='me', comment='Separate scopes with a space'))
    op.add_column('tokens', sa.Column('scopes', sa.String(2000), nullable=False, server_default='me', comment='Separate scopes with a space'))
    op.drop_column('users', 'level')
    op.drop_column('tokens', 'user_level')


def downgrade():
    pass
