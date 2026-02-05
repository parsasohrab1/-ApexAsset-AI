"""Add performance indexes for dashboard and alert queries (optional; included in 000_initial)

Revision ID: 001_add_indexes
Revises: 000_initial
Create Date: 2025-02-05

Indexes are already created in 000_initial_schema. This revision exists for
databases that were created before 000_initial and may need these indexes.
Uses IF NOT EXISTS for idempotency.
"""
from alembic import op

# revision identifiers
revision = "001_add_indexes"
down_revision = "000_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Indexes already in 000_initial; use IF NOT EXISTS for idempotency on legacy DBs
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_asset_status ON assets (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_alert_status ON alerts (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_alert_severity ON alerts (severity)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_alert_occurred_at ON alerts (occurred_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_alert_severity_status_occurred "
        "ON alerts (severity, status, occurred_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_asset_status")
    op.execute("DROP INDEX IF EXISTS idx_alert_status")
    op.execute("DROP INDEX IF EXISTS idx_alert_severity")
    op.execute("DROP INDEX IF EXISTS idx_alert_occurred_at")
    op.execute("DROP INDEX IF EXISTS idx_alert_severity_status_occurred")
