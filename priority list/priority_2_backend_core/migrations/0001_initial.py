"""initial Phase 3 schema (baseline from models metadata)

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-24
"""
from alembic import op

from app.db.base import Base
from app.db import models  # noqa: F401  (populates metadata)

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Baseline: create the full normalized schema from the model metadata.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
