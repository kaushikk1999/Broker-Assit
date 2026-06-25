"""phase 4 — ingestion_runs bookkeeping table (additive, reversible)

Revision ID: 0002_phase4_ingestion
Revises: 0001_initial
Create Date: 2026-06-25

Guarded so it is safe in both directions: 0001 builds the baseline via ``create_all`` over the *current*
model metadata, so on a fresh database ``ingestion_runs`` already exists by the time this runs (no-op);
on a database that was stamped at 0001 *before* this table existed, it is created here.
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_phase4_ingestion"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "ingestion_runs" in insp.get_table_names():
        return
    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("mode", sa.String(length=12), server_default="fixture", nullable=False),
        sa.Column("status", sa.String(length=12), server_default="running", nullable=False),
        sa.Column("discovered", sa.Integer(), server_default="0", nullable=False),
        sa.Column("registered", sa.Integer(), server_default="0", nullable=False),
        sa.Column("versioned", sa.Integer(), server_default="0", nullable=False),
        sa.Column("duplicates", sa.Integer(), server_default="0", nullable=False),
        sa.Column("chunks_written", sa.Integer(), server_default="0", nullable=False),
        sa.Column("errors", sa.Integer(), server_default="0", nullable=False),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_ingestion_runs_source", "ingestion_runs", ["source"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "ingestion_runs" not in insp.get_table_names():
        return
    if any(ix["name"] == "ix_ingestion_runs_source"
           for ix in insp.get_indexes("ingestion_runs")):
        op.drop_index("ix_ingestion_runs_source", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
