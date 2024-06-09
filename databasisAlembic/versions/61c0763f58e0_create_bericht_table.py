"""create Bericht table

Revision ID: 61c0763f58e0
Revises: 
Create Date: 2024-06-02 21:27:06.190940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "61c0763f58e0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "Bericht", sa.Column("id", sa.VARCHAR, primary_key=True, nullable=False),
        sa.Column("titel", sa.VARCHAR, nullable=False)
    )


def downgrade() -> None:
    op.drop_table("Bericht")