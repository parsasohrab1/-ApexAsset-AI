"""
ETL Pipeline for importing synthetic data into the database
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..db_models import (
    Asset, Alert, MaintenanceRecord, ProductionData, SensorReading,
    AssetType, AssetStatus, AlertSeverity, AlertStatus, MaintenanceType
)
from ..influxdb_client import influxdb_manager
from influxdb_client import Point


class DataImporter:
    """Import data from CSV files into the database"""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize importer with database session"""
        self.db = db or SessionLocal()
        self.own_session = db is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.own_session:
            self.db.close()
    
    def import_production_data(self, csv_path: str) -> int:
        """
        Import production data from CSV
        
        Args:
            csv_path: Path to production data CSV file
            
        Returns:
            Number of records imported
        """
        print(f"Importing production data from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get or create assets (wells)
        asset_map = {}
        for well_id in df['well_id'].unique():
            # Check if asset exists
            asset = self.db.query(Asset).filter(Asset.name == well_id).first()
            if not asset:
                # Create new well asset
                asset = Asset(
                    name=well_id,
                    asset_type=AssetType.WELL,
                    description=f"Production well {well_id}",
                    status=AssetStatus.ACTIVE
                )
                self.db.add(asset)
                self.db.flush()
            asset_map[well_id] = asset.id
        
        # Import production records
        count = 0
        for _, row in df.iterrows():
            prod_record = ProductionData(
                asset_id=asset_map[row['well_id']],
                production_date=row['date'],
                duration_hours=24.0,
                oil_production=row['oil_rate'] * row['uptime_hours'] / 24,
                gas_production=row['gas_rate'] * row['uptime_hours'] / 24,
                water_production=row['water_rate'] * row['uptime_hours'] / 24,
                oil_rate=row['oil_rate'],
                gas_rate=row['gas_rate'],
                water_cut=row['water_cut'],
                wellhead_pressure=row['wellhead_pressure'],
                uptime_hours=row['uptime_hours'],
                downtime_hours=row['downtime_hours'],
                data_source='synthetic',
                data_quality='good'
            )
            self.db.add(prod_record)
            count += 1
        
        self.db.commit()
        print(f"  ✓ Imported {count} production records")
        return count
    
    def import_alert_events(self, csv_path: str) -> int:
        """
        Import alert events from CSV
        
        Args:
            csv_path: Path to alert events CSV file
            
        Returns:
            Number of alerts imported
        """
        print(f"Importing alert events from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get or create assets
        asset_map = {}
        for asset_id in df['asset_id'].unique():
            asset = self.db.query(Asset).filter(Asset.name == asset_id).first()
            if not asset:
                # Create generic asset
                asset = Asset(
                    name=asset_id,
                    asset_type=AssetType.COMPRESSOR,  # Default type
                    description=f"Asset {asset_id}",
                    status=AssetStatus.ACTIVE
                )
                self.db.add(asset)
                self.db.flush()
            asset_map[asset_id] = asset.id
        
        # Map severity levels
        severity_map = {
            'low': AlertSeverity.LOW,
            'medium': AlertSeverity.MEDIUM,
            'high': AlertSeverity.HIGH,
            'critical': AlertSeverity.CRITICAL
        }
        
        # Import alerts
        count = 0
        for _, row in df.iterrows():
            alert = Alert(
                title=row['alert_type'],
                description=row['description'],
                severity=severity_map.get(row['severity'], AlertSeverity.MEDIUM),
                status=AlertStatus.OPEN if count % 3 == 0 else AlertStatus.RESOLVED,  # Some open, some resolved
                asset_id=asset_map[row['asset_id']],
                alert_type=row['category'],
                source='system',
                threshold_value=row['threshold_value'] if row['threshold_value'] != 0 else None,
                actual_value=row['actual_value'] if row['actual_value'] != 0 else None,
                occurred_at=row['timestamp'],
                resolved_at=row['timestamp'] + pd.Timedelta(hours=2) if count % 3 != 0 else None
            )
            self.db.add(alert)
            count += 1
        
        self.db.commit()
        print(f"  ✓ Imported {count} alert events")
        return count
    
    def import_maintenance_events(self, csv_path: str) -> int:
        """
        Import maintenance events from CSV
        
        Args:
            csv_path: Path to maintenance events CSV file
            
        Returns:
            Number of maintenance records imported
        """
        print(f"Importing maintenance events from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['start_date'] = pd.to_datetime(df['start_date'])
        
        # Get or create assets
        asset_map = {}
        for asset_id in df['asset_id'].unique():
            asset = self.db.query(Asset).filter(Asset.name == asset_id).first()
            if not asset:
                asset = Asset(
                    name=asset_id,
                    asset_type=AssetType.COMPRESSOR,
                    description=f"Asset {asset_id}",
                    status=AssetStatus.ACTIVE
                )
                self.db.add(asset)
                self.db.flush()
            asset_map[asset_id] = asset.id
        
        # Map maintenance types
        type_map = {
            'Preventive Maintenance': MaintenanceType.PREVENTIVE,
            'Inspection': MaintenanceType.PREVENTIVE,
            'Corrective Maintenance': MaintenanceType.CORRECTIVE,
            'Calibration': MaintenanceType.PREVENTIVE,
            'Repair': MaintenanceType.CORRECTIVE
        }
        
        # Import maintenance records
        count = 0
        for _, row in df.iterrows():
            completed_date = row['start_date'] + pd.Timedelta(hours=row['duration_hours'])
            
            maint_record = MaintenanceRecord(
                asset_id=asset_map[row['asset_id']],
                maintenance_type=type_map.get(row['maintenance_type'], MaintenanceType.CORRECTIVE),
                title=row['maintenance_type'],
                description=f"{row['maintenance_type']} - {row['schedule_type']}",
                scheduled_date=row['start_date'],
                completed_date=completed_date,
                work_performed=f"Completed {row['maintenance_type']}",
                labor_hours=row['duration_hours'],
                cost=row['cost'],
                performed_by=row['technician']
            )
            self.db.add(maint_record)
            count += 1
        
        self.db.commit()
        print(f"  ✓ Imported {count} maintenance records")
        return count
    
    def import_sensor_timeseries(self, csv_path: str, sample_rate: int = 60) -> int:
        """
        Import time-series sensor data
        For high-frequency data (1Hz), we sample it down and store aggregates in PostgreSQL
        Full 1Hz data would go to InfluxDB
        
        Args:
            csv_path: Path to sensor timeseries CSV file
            sample_rate: Sample every N seconds for PostgreSQL (default 60s)
            
        Returns:
            Number of aggregated records imported
        """
        print(f"Importing sensor timeseries from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get sensor columns
        sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
        
        # Get or create a default asset for sensors
        asset = self.db.query(Asset).filter(Asset.name == 'sensor_platform').first()
        if not asset:
            asset = Asset(
                name='sensor_platform',
                asset_type=AssetType.PLATFORM,
                description='Sensor monitoring platform',
                status=AssetStatus.ACTIVE
            )
            self.db.add(asset)
            self.db.flush()
        
        # Sample data (every N seconds) and store aggregates
        df_sampled = df.set_index('timestamp').resample(f'{sample_rate}S').agg({
            col: ['mean', 'min', 'max', 'std', 'count'] for col in sensor_cols
        })
        
        count = 0
        for timestamp, row in df_sampled.iterrows():
            for sensor_col in sensor_cols:
                if pd.notna(row[(sensor_col, 'mean')]):
                    sensor_reading = SensorReading(
                        asset_id=asset.id,
                        sensor_id=sensor_col,
                        sensor_type='process',
                        reading_time=timestamp,
                        value=None,  # Using aggregates instead
                        unit='units',
                        quality_flag='good',
                        min_value=row[(sensor_col, 'min')],
                        max_value=row[(sensor_col, 'max')],
                        avg_value=row[(sensor_col, 'mean')],
                        std_dev=row[(sensor_col, 'std')],
                        sample_count=int(row[(sensor_col, 'count')])
                    )
                    self.db.add(sensor_reading)
                    count += 1
        
        self.db.commit()
        print(f"  ✓ Imported {count} aggregated sensor readings")
        return count
    
    def import_to_influxdb(self, csv_path: str, measurement: str = 'sensor_data') -> int:
        """
        Import high-frequency sensor data to InfluxDB
        
        Args:
            csv_path: Path to sensor timeseries CSV file
            measurement: InfluxDB measurement name
            
        Returns:
            Number of points written
        """
        print(f"Importing sensor data to InfluxDB from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get sensor columns
        sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
        
        # Prepare points for batch write
        points = []
        for _, row in df.iterrows():
            for sensor_col in sensor_cols:
                if pd.notna(row[sensor_col]):
                    point = Point(measurement) \
                        .tag("sensor_id", sensor_col) \
                        .tag("asset_id", "sensor_platform") \
                        .field("value", float(row[sensor_col])) \
                        .time(row['timestamp'])
                    points.append(point)
        
        # Write in batches
        batch_size = 5000
        total_written = 0
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            influxdb_manager.write_batch_sensor_data(batch)
            total_written += len(batch)
        
        print(f"  ✓ Imported {total_written} points to InfluxDB")
        return total_written
    
    def import_all_from_directory(self, data_dir: str) -> Dict[str, int]:
        """
        Import all CSV files from a directory
        
        Args:
            data_dir: Path to directory containing CSV files
            
        Returns:
            Dictionary with import statistics
        """
        data_path = Path(data_dir)
        stats = {}
        
        print("=" * 60)
        print("Starting ETL Import Process")
        print("=" * 60)
        
        # Import production data
        prod_file = data_path / 'production_data_30d.csv'
        if prod_file.exists():
            stats['production'] = self.import_production_data(str(prod_file))
        
        # Import alerts
        alert_file = data_path / 'alert_events_30d.csv'
        if alert_file.exists():
            stats['alerts'] = self.import_alert_events(str(alert_file))
        
        # Import maintenance
        maint_file = data_path / 'maintenance_events_180d.csv'
        if maint_file.exists():
            stats['maintenance'] = self.import_maintenance_events(str(maint_file))
        
        # Import sensor data (aggregated)
        sensor_file = data_path / 'sensor_timeseries_1h.csv'
        if sensor_file.exists():
            stats['sensor_aggregates'] = self.import_sensor_timeseries(str(sensor_file))
            
            # Also import to InfluxDB if configured
            try:
                stats['influxdb_points'] = self.import_to_influxdb(str(sensor_file))
            except Exception as e:
                print(f"  ⚠️  InfluxDB import skipped: {e}")
                stats['influxdb_points'] = 0
        
        print("\n" + "=" * 60)
        print("ETL Import Complete!")
        print("=" * 60)
        for key, value in stats.items():
            print(f"  {key}: {value:,} records")
        print("=" * 60)
        
        return stats


def run_etl_pipeline(data_dir: str = 'sample_data'):
    """Run the complete ETL pipeline"""
    with DataImporter() as importer:
        stats = importer.import_all_from_directory(data_dir)
        return stats


if __name__ == "__main__":
    # Generate sample data first
    from ..data_generator.synthetic_data_generator import generate_sample_dataset
    
    print("Step 1: Generating sample data...")
    generate_sample_dataset('sample_data')
    
    print("\nStep 2: Running ETL import...")
    run_etl_pipeline('sample_data')
