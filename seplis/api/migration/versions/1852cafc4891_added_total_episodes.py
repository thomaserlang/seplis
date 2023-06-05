"""added total episodes

Revision ID: 1852cafc4891
Revises: 238440685e7c
Create Date: 2019-04-11 21:06:13.727004

"""

# revision identifiers, used by Alembic.
revision = '1852cafc4891'
down_revision = '238440685e7c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('shows',
        sa.Column('total_episodes', sa.Integer, server_default='0')
    )
    conn = op.get_bind()
    conn.execute(sa.text('''
        UPDATE 
            shows s, 
            (select show_id, count(number) as total_episodes FROM episodes GROUP BY show_id) e
        SET
            s.total_episodes=e.total_episodes
        WHERE
            e.show_id=s.id;
    '''))

def downgrade():
    pass
