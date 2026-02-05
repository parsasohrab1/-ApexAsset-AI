from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal, engine, Base
from .config import settings
from .db_models import (
    User, Asset, Alert, MaintenanceRecord, WorkOrder,
    UserRole, AssetType, AssetStatus, AlertSeverity, AlertStatus,
    MaintenanceType, WorkOrderStatus, WorkOrderPriority
)
from .services.auth_service import AuthService


def init_database():
    """Initialize database with tables. In production, use Alembic instead."""
    if settings.ENVIRONMENT == "production":
        print(
            "⚠️  Production mode: Skipping create_all. "
            "Run 'alembic upgrade head' to apply migrations."
        )
        return
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def seed_database():
    """Seed database with initial data"""
    db = SessionLocal()
    
    try:
        print("Seeding database with initial data...")
        
        # Create admin user
        auth_service = AuthService(db)
        admin_email = "admin@apexasset.com"
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            from .models import UserCreate
            admin_user = UserCreate(
                email=admin_email,
                full_name="System Administrator",
                role=UserRole.ADMIN,
                password="admin123",  # Change this in production!
                is_active=True
            )
            auth_service.create_user(admin_user)
            print(f"✓ Created admin user: {admin_email}")
        
        # Create sample users
        sample_users = [
            {
                "email": "operator@apexasset.com",
                "full_name": "Field Operator",
                "role": UserRole.FIELD_OPERATOR,
                "password": "operator123"
            },
            {
                "email": "engineer@apexasset.com",
                "full_name": "Production Engineer",
                "role": UserRole.PRODUCTION_ENGINEER,
                "password": "engineer123"
            },
            {
                "email": "maintenance@apexasset.com",
                "full_name": "Maintenance Tech",
                "role": UserRole.MAINTENANCE_TECH,
                "password": "maint123"
            }
        ]
        
        for user_data in sample_users:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                from .models import UserCreate
                user = UserCreate(**user_data, is_active=True)
                auth_service.create_user(user)
                print(f"✓ Created user: {user_data['email']}")
        
        # Create sample assets
        if db.query(Asset).count() == 0:
            # Platform (parent asset)
            platform = Asset(
                name="Platform Alpha",
                asset_type=AssetType.PLATFORM,
                description="Main production platform",
                status=AssetStatus.ACTIVE,
                latitude=29.5,
                longitude=48.0,
                location_name="Persian Gulf",
                specifications={
                    "capacity": "50,000 bbl/day",
                    "wells": 12,
                    "installation_year": 2015
                }
            )
            db.add(platform)
            db.flush()
            
            # Wells (child assets)
            wells = [
                Asset(
                    name=f"Well A-{i}",
                    asset_type=AssetType.WELL,
                    description=f"Production well {i}",
                    status=AssetStatus.ACTIVE,
                    parent_id=platform.id,
                    specifications={
                        "depth": 3500 + i * 100,
                        "type": "producer",
                        "completion": "horizontal"
                    }
                )
                for i in range(1, 6)
            ]
            db.add_all(wells)
            
            # Process equipment
            equipment = [
                Asset(
                    name="Separator Unit 1",
                    asset_type=AssetType.SEPARATOR,
                    description="Three-phase separator",
                    status=AssetStatus.ACTIVE,
                    parent_id=platform.id,
                    manufacturer="Cameron",
                    model="SEP-3000"
                ),
                Asset(
                    name="Gas Compressor A1",
                    asset_type=AssetType.COMPRESSOR,
                    description="Main gas compressor",
                    status=AssetStatus.ACTIVE,
                    parent_id=platform.id,
                    manufacturer="GE Oil & Gas",
                    model="COMP-5000"
                ),
                Asset(
                    name="Export Pump P-101",
                    asset_type=AssetType.PUMP,
                    description="Crude oil export pump",
                    status=AssetStatus.ACTIVE,
                    parent_id=platform.id,
                    manufacturer="Flowserve",
                    model="PUMP-2500"
                )
            ]
            db.add_all(equipment)
            db.flush()
            
            print(f"✓ Created {len(wells) + len(equipment) + 1} sample assets")
            
            # Create sample alerts
            compressor = [e for e in equipment if e.asset_type == AssetType.COMPRESSOR][0]
            separator = [e for e in equipment if e.asset_type == AssetType.SEPARATOR][0]
            
            alerts = [
                Alert(
                    title="Compressor A1 vibration high",
                    description="Vibration levels exceeding normal operating range",
                    severity=AlertSeverity.HIGH,
                    status=AlertStatus.OPEN,
                    asset_id=compressor.id,
                    alert_type="vibration",
                    source="system",
                    threshold_value=5.0,
                    actual_value=7.2,
                    occurred_at=datetime.utcnow() - timedelta(minutes=5)
                ),
                Alert(
                    title="Separator pressure spike",
                    description="Pressure spike detected in separator unit",
                    severity=AlertSeverity.MEDIUM,
                    status=AlertStatus.ACKNOWLEDGED,
                    asset_id=separator.id,
                    alert_type="pressure",
                    source="system",
                    threshold_value=150.0,
                    actual_value=165.0,
                    occurred_at=datetime.utcnow() - timedelta(minutes=22),
                    acknowledged_at=datetime.utcnow() - timedelta(minutes=10)
                )
            ]
            db.add_all(alerts)
            print(f"✓ Created {len(alerts)} sample alerts")
            
            # Create sample maintenance record
            maintenance = MaintenanceRecord(
                asset_id=compressor.id,
                maintenance_type=MaintenanceType.PREVENTIVE,
                title="Quarterly inspection",
                description="Routine quarterly inspection and servicing",
                scheduled_date=datetime.utcnow() + timedelta(days=7),
                performed_by="Maintenance Team",
                labor_hours=4.0,
                cost=2500.0
            )
            db.add(maintenance)
            print("✓ Created sample maintenance record")
            
            # Create sample work order
            work_order = WorkOrder(
                work_order_number="WO-2024-001",
                asset_id=compressor.id,
                title="Inspect compressor vibration",
                description="Investigate and resolve high vibration alert",
                priority=WorkOrderPriority.HIGH,
                status=WorkOrderStatus.PENDING,
                scheduled_start=datetime.utcnow() + timedelta(hours=2),
                scheduled_end=datetime.utcnow() + timedelta(hours=6),
                estimated_hours=4.0,
                estimated_cost=1500.0
            )
            db.add(work_order)
            print("✓ Created sample work order")
        
        db.commit()
        print("\n✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("ApexAsset AI - Database Initialization")
    print("=" * 60)
    
    init_database()
    seed_database()
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print("\nDefault credentials:")
    print("  Admin: admin@apexasset.com / admin123")
    print("  Operator: operator@apexasset.com / operator123")
    print("  Engineer: engineer@apexasset.com / engineer123")
    print("  Maintenance: maintenance@apexasset.com / maint123")
    print("\n⚠️  Please change these passwords in production!")
    print("=" * 60)
