"""add author_id to news

Revision ID: 2707f3274c9b
Revises: 3062b0edb2dd
Create Date: 2026-08-04 23:24:15.715605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2707f3274c9b'
down_revision: Union[str, Sequence[str], None] = '3062b0edb2dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Column starts nullable so pre-existing news rows (from manual/dev
    # testing) can be backfilled before the NOT NULL constraint is applied.
    op.add_column('news', sa.Column('author_id', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE news SET author_id = (SELECT id FROM employees ORDER BY id LIMIT 1) "
        "WHERE author_id IS NULL"
    )
    op.alter_column('news', 'author_id', nullable=False)
    op.create_foreign_key(
        'fk_news_author_id_employees', 'news', 'employees', ['author_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_news_author_id_employees', 'news', type_='foreignkey')
    op.drop_column('news', 'author_id')
