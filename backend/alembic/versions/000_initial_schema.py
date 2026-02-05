"""Initial schema: users, assets, alerts, maintenance_records, work_orders, production_data, sensor_readings

Revision ID: 000_initial
Revises:
Create Date: 2025-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "000_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("field_operator", "maintenance_technician", "production_engineer", "reservoir_engineer", "hse_manager", "asset_manager", "data_scientist", "executive", "admin", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Assets
    op.create_table(
        "assets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("asset_type", sa.Enum("well", "separator", "compressor", "pump", "heat_exchanger", "pipeline", "storage_tank", "platform", "facility", name="assettype"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("active", "inactive", "maintenance", "decommissioned", name="assetstatus"), nullable=False, server_default="active"),
        sa.Column("parent_id", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("elevation", sa.Float(), nullable=True),
        sa.Column("location_name", sa.String(255), nullable=True),
        sa.Column("specifications", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(255), nullable=True),
        sa.Column("installation_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("commissioning_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_asset_parent", "assets", ["parent_id"])
    op.create_index("idx_asset_status", "assets", ["status"])
    op.create_index("idx_asset_type_status", "assets", ["asset_type", "status"])

    # Alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("severity", sa.Enum("low", "medium", "high", "critical", name="alertseverity"), nullable=False),
        sa.Column("status", sa.Enum("open", "acknowledged", "in_progress", "resolved", "closed", name="alertstatus"), nullable=False, server_default="open"),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("assigned_to", sa.String(), nullable=True),
        sa.Column("alert_type", sa.String(100), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("actual_value", sa.Float(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_alert_asset_severity", "alerts", ["asset_id", "severity"])
    op.create_index("idx_alert_occurred_at", "alerts", ["occurred_at"])
    op.create_index("idx_alert_severity", "alerts", ["severity"])
    op.create_index("idx_alert_severity_status_occurred", "alerts", ["severity", "status", "occurred_at"])
    op.create_index("idx_alert_status", "alerts", ["status"])
    op.create_index("idx_alert_status_occurred", "alerts", ["status", "occurred_at"])

    # Maintenance records
    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("maintenance_type", sa.Enum("preventive", "predictive", "corrective", "breakdown", name="maintenancetype"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("work_performed", sa.Text(), nullable=True),
        sa.Column("parts_replaced", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("labor_hours", sa.Float(), nullable=True),
        sa.Column("cost", sa.Float(), nullable=True),
        sa.Column("performed_by", sa.String(255), nullable=True),
        sa.Column("supervised_by", sa.String(255), nullable=True),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("next_maintenance_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_maint_asset_type", "maintenance_records", ["asset_id", "maintenance_type"])
    op.create_index("idx_maint_scheduled", "maintenance_records", ["scheduled_date"])

    # Work orders
    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("work_order_number", sa.String(50), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("assigned_to", sa.String(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Enum("low", "medium", "high", "critical", name="workorderpriority"), nullable=False, server_default="medium"),
        sa.Column("status", sa.Enum("pending", "scheduled", "in_progress", "completed", "cancelled", name="workorderstatus"), nullable=False, server_default="pending"),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_hours", sa.Float(), nullable=True),
        sa.Column("actual_hours", sa.Float(), nullable=True),
        sa.Column("estimated_cost", sa.Float(), nullable=True),
        sa.Column("actual_cost", sa.Float(), nullable=True),
        sa.Column("materials_required", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("completion_percentage", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("work_order_number"),
    )
    op.create_index("idx_wo_asset_status", "work_orders", ["asset_id", "status"])
    op.create_index("idx_wo_number", "work_orders", ["work_order_number"])
    op.create_index("idx_wo_priority_status", "work_orders", ["priority", "status"])

    # Production data
    op.create_table(
        "production_data",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("production_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_hours", sa.Float(), nullable=True),
        sa.Column("oil_production", sa.Float(), nullable=True),
        sa.Column("gas_production", sa.Float(), nullable=True),
        sa.Column("water_production", sa.Float(), nullable=True),
        sa.Column("oil_rate", sa.Float(), nullable=True),
        sa.Column("gas_rate", sa.Float(), nullable=True),
        sa.Column("water_cut", sa.Float(), nullable=True),
        sa.Column("gor", sa.Float(), nullable=True),
        sa.Column("wellhead_pressure", sa.Float(), nullable=True),
        sa.Column("flowing_pressure", sa.Float(), nullable=True),
        sa.Column("static_pressure", sa.Float(), nullable=True),
        sa.Column("wellhead_temperature", sa.Float(), nullable=True),
        sa.Column("separator_temperature", sa.Float(), nullable=True),
        sa.Column("uptime_hours", sa.Float(), nullable=True),
        sa.Column("downtime_hours", sa.Float(), nullable=True),
        sa.Column("downtime_reason", sa.String(255), nullable=True),
        sa.Column("data_source", sa.String(100), nullable=True),
        sa.Column("data_quality", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_prod_asset_date", "production_data", ["asset_id", "production_date"])

    # Sensor readings
    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("sensor_id", sa.String(100), nullable=False),
        sa.Column("sensor_type", sa.String(100), nullable=False),
        sa.Column("reading_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("quality_flag", sa.String(50), nullable=True),
        sa.Column("min_value", sa.Float(), nullable=True),
        sa.Column("max_value", sa.Float(), nullable=True),
        sa.Column("avg_value", sa.Float(), nullable=True),
        sa.Column("std_dev", sa.Float(), nullable=True),
        sa.Column("sample_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sensor_asset_time", "sensor_readings", ["asset_id", "reading_time"])
    op.create_index("idx_sensor_type_time", "sensor_readings", ["sensor_type", "reading_time"])


def downgrade() -> None:
    op.drop_table("sensor_readings")
    op.drop_table("production_data")
    op.drop_table("work_orders")
    op.drop_table("maintenance_records")
    op.drop_table("alerts")
    op.drop_table("assets")
    op.drop_table("users")

    # Drop enum types (PostgreSQL)
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")
    op.execute("DROP TYPE IF EXISTS assettype CASCADE")
    op.execute("DROP TYPE IF EXISTS assetstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS alertseverity CASCADE")
    op.execute("DROP TYPE IF EXISTS alertstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS maintenancetype CASCADE")
    op.execute("DROP TYPE IF EXISTS workorderpriority CASCADE")
    op.execute("DROP TYPE IF EXISTS workorderstatus CASCADE")
