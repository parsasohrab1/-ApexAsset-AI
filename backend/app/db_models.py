from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from .database import Base


def generate_uuid():
    return str(uuid.uuid4())


# Enums
class UserRole(str, enum.Enum):
    FIELD_OPERATOR = "field_operator"
    MAINTENANCE_TECH = "maintenance_technician"
    PRODUCTION_ENGINEER = "production_engineer"
    RESERVOIR_ENGINEER = "reservoir_engineer"
    HSE_MANAGER = "hse_manager"
    ASSET_MANAGER = "asset_manager"
    DATA_SCIENTIST = "data_scientist"
    EXECUTIVE = "executive"
    ADMIN = "admin"


class AssetType(str, enum.Enum):
    WELL = "well"
    SEPARATOR = "separator"
    COMPRESSOR = "compressor"
    PUMP = "pump"
    HEAT_EXCHANGER = "heat_exchanger"
    PIPELINE = "pipeline"
    STORAGE_TANK = "storage_tank"
    PLATFORM = "platform"
    FACILITY = "facility"


class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MaintenanceType(str, enum.Enum):
    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    BREAKDOWN = "breakdown"


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    alerts_created = relationship("Alert", back_populates="created_by_user", foreign_keys="Alert.created_by")
    work_orders = relationship("WorkOrder", back_populates="assigned_to_user")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.ACTIVE, nullable=False)
    
    # Hierarchy
    parent_id = Column(String, ForeignKey("assets.id"), nullable=True)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    location_name = Column(String(255))
    
    # Technical specifications
    specifications = Column(JSON)
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    installation_date = Column(DateTime(timezone=True))
    commissioning_date = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("Asset", remote_side=[id], backref="children")
    alerts = relationship("Alert", back_populates="asset")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset")
    work_orders = relationship("WorkOrder", back_populates="asset")
    
    # Indexes
    __table_args__ = (
        Index('idx_asset_type_status', 'asset_type', 'status'),
        Index('idx_asset_parent', 'parent_id'),
        Index('idx_asset_status', 'status'),  # dashboard count by status
    )


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN, nullable=False)
    
    # Asset relationship
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    
    # User relationships
    created_by = Column(String, ForeignKey("users.id"))
    assigned_to = Column(String, ForeignKey("users.id"))
    
    # Alert details
    alert_type = Column(String(100))
    source = Column(String(100))  # system, user, ai_model
    threshold_value = Column(Float)
    actual_value = Column(Float)
    
    # Timestamps
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Action taken
    action_taken = Column(Text)
    resolution_notes = Column(Text)
    
    # Relationships
    asset = relationship("Asset", back_populates="alerts")
    created_by_user = relationship("User", back_populates="alerts_created", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_asset_severity', 'asset_id', 'severity'),
        Index('idx_alert_status_occurred', 'status', 'occurred_at'),  # open alerts, list by status
        Index('idx_alert_status', 'status'),  # count by status (dashboard)
        Index('idx_alert_severity', 'severity'),  # filter by severity
        Index('idx_alert_occurred_at', 'occurred_at'),  # ORDER BY, time-range queries
        Index('idx_alert_severity_status_occurred', 'severity', 'status', 'occurred_at'),  # critical alerts
    )


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True))
    completed_date = Column(DateTime(timezone=True))
    
    # Technical details
    work_performed = Column(Text)
    parts_replaced = Column(JSON)
    labor_hours = Column(Float)
    cost = Column(Float)
    
    # Personnel
    performed_by = Column(String(255))
    supervised_by = Column(String(255))
    
    # Results
    findings = Column(Text)
    recommendations = Column(Text)
    next_maintenance_date = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_maint_asset_type', 'asset_id', 'maintenance_type'),
        Index('idx_maint_scheduled', 'scheduled_date'),
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    work_order_number = Column(String(50), unique=True, nullable=False)
    
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(WorkOrderPriority), default=WorkOrderPriority.MEDIUM, nullable=False)
    status = Column(SQLEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING, nullable=False)
    
    # Scheduling
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Resources
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    materials_required = Column(JSON)
    
    # Completion
    completion_notes = Column(Text)
    completion_percentage = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="work_orders")
    assigned_to_user = relationship("User", back_populates="work_orders")
    
    # Indexes
    __table_args__ = (
        Index('idx_wo_asset_status', 'asset_id', 'status'),
        Index('idx_wo_priority_status', 'priority', 'status'),
        Index('idx_wo_number', 'work_order_number'),
    )


class ProductionData(Base):
    __tablename__ = "production_data"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    
    # Time period
    production_date = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Float)
    
    # Production volumes
    oil_production = Column(Float)  # barrels
    gas_production = Column(Float)  # MCF
    water_production = Column(Float)  # barrels
    
    # Rates
    oil_rate = Column(Float)  # bbl/day
    gas_rate = Column(Float)  # MCF/day
    water_cut = Column(Float)  # percentage
    gor = Column(Float)  # gas-oil ratio
    
    # Pressures
    wellhead_pressure = Column(Float)
    flowing_pressure = Column(Float)
    static_pressure = Column(Float)
    
    # Temperatures
    wellhead_temperature = Column(Float)
    separator_temperature = Column(Float)
    
    # Status
    uptime_hours = Column(Float)
    downtime_hours = Column(Float)
    downtime_reason = Column(String(255))
    
    # Metadata
    data_source = Column(String(100))
    data_quality = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_prod_asset_date', 'asset_id', 'production_date'),
    )


class SensorReading(Base):
    """For aggregated sensor data (not real-time 1Hz data which goes to InfluxDB)"""
    __tablename__ = "sensor_readings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    
    sensor_id = Column(String(100), nullable=False)
    sensor_type = Column(String(100), nullable=False)
    
    # Time
    reading_time = Column(DateTime(timezone=True), nullable=False)
    
    # Values
    value = Column(Float)
    unit = Column(String(50))
    
    # Quality
    quality_flag = Column(String(50))
    
    # Statistical aggregates (for rolled-up data)
    min_value = Column(Float)
    max_value = Column(Float)
    avg_value = Column(Float)
    std_dev = Column(Float)
    sample_count = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_sensor_asset_time', 'asset_id', 'reading_time'),
        Index('idx_sensor_type_time', 'sensor_type', 'reading_time'),
    )
