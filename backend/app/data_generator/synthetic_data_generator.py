"""
Synthetic Data Generator for ApexAsset AI
Generates realistic sensor data, production data, and events for testing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class SyntheticDataGenerator:
    """Generate synthetic data for oil & gas assets"""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility"""
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_time_series(
        self,
        start_time: datetime,
        duration_days: int,
        frequency_hz: float = 1.0,
        num_sensors: int = 10
    ) -> pd.DataFrame:
        """
        Generate time-series sensor data
        
        Args:
            start_time: Start timestamp
            duration_days: Duration in days
            frequency_hz: Sampling frequency in Hz
            num_sensors: Number of sensors
            
        Returns:
            DataFrame with timestamp and sensor readings
        """
        # Calculate total samples
        total_seconds = duration_days * 24 * 3600
        total_samples = int(total_seconds * frequency_hz)
        
        # Generate timestamps
        timestamps = pd.date_range(
            start=start_time,
            periods=total_samples,
            freq=f'{int(1000/frequency_hz)}ms'
        )
        
        data = {'timestamp': timestamps}
        
        # Generate sensor data with realistic patterns
        for i in range(num_sensors):
            sensor_name = f'sensor_{i:03d}'
            
            # Base value with daily and hourly patterns
            t = np.arange(total_samples) / (3600 * frequency_hz)  # Time in hours
            daily_pattern = 5 * np.sin(2 * np.pi * t / 24)  # Daily cycle
            weekly_pattern = 2 * np.sin(2 * np.pi * t / (24 * 7))  # Weekly cycle
            noise = np.random.normal(0, 0.5, total_samples)
            
            # Different base values for different sensors
            base_value = 50 + i * 10
            
            sensor_data = base_value + daily_pattern + weekly_pattern + noise
            
            # Add occasional spikes (anomalies)
            spike_indices = np.random.choice(
                total_samples,
                size=int(total_samples * 0.001),  # 0.1% spikes
                replace=False
            )
            sensor_data[spike_indices] += np.random.uniform(20, 50, len(spike_indices))
            
            data[sensor_name] = sensor_data
        
        return pd.DataFrame(data)
    
    def generate_production_data(
        self,
        start_date: datetime,
        duration_days: int,
        num_wells: int = 5
    ) -> pd.DataFrame:
        """
        Generate daily production data for wells
        
        Args:
            start_date: Start date
            duration_days: Number of days
            num_wells: Number of wells
            
        Returns:
            DataFrame with daily production data
        """
        dates = pd.date_range(start=start_date, periods=duration_days, freq='D')
        
        records = []
        for well_id in range(1, num_wells + 1):
            # Base production with decline
            initial_oil_rate = np.random.uniform(100, 500)  # bbl/day
            initial_gas_rate = np.random.uniform(500, 2000)  # MCF/day
            decline_rate = np.random.uniform(0.001, 0.005)  # per day
            
            for idx, date in enumerate(dates):
                # Exponential decline
                oil_rate = initial_oil_rate * np.exp(-decline_rate * idx)
                gas_rate = initial_gas_rate * np.exp(-decline_rate * idx)
                
                # Add daily variation
                oil_rate *= np.random.uniform(0.9, 1.1)
                gas_rate *= np.random.uniform(0.9, 1.1)
                
                # Water production increasing over time
                water_cut = min(0.9, 0.1 + idx * 0.001)
                water_rate = oil_rate * water_cut / (1 - water_cut)
                
                # Pressures declining
                wellhead_pressure = 1000 * np.exp(-decline_rate * idx * 2) + np.random.normal(0, 10)
                
                # Calculate uptime (with occasional downtime)
                uptime = 24 if np.random.random() > 0.05 else np.random.uniform(0, 24)
                
                records.append({
                    'date': date,
                    'well_id': f'well_{well_id:02d}',
                    'oil_rate': round(oil_rate, 2),
                    'gas_rate': round(gas_rate, 2),
                    'water_rate': round(water_rate, 2),
                    'water_cut': round(water_cut * 100, 2),
                    'wellhead_pressure': round(wellhead_pressure, 1),
                    'uptime_hours': round(uptime, 1),
                    'downtime_hours': round(24 - uptime, 1)
                })
        
        return pd.DataFrame(records)
    
    def generate_alert_events(
        self,
        start_time: datetime,
        duration_days: int,
        num_assets: int = 10,
        avg_alerts_per_day: float = 2.0
    ) -> pd.DataFrame:
        """
        Generate alert/alarm events
        
        Args:
            start_time: Start timestamp
            duration_days: Duration in days
            num_assets: Number of assets
            avg_alerts_per_day: Average alerts per day
            
        Returns:
            DataFrame with alert events
        """
        total_alerts = int(duration_days * avg_alerts_per_day)
        
        alert_types = [
            ('High Temperature', ['high', 'critical'], 'temperature'),
            ('High Pressure', ['high', 'critical'], 'pressure'),
            ('High Vibration', ['medium', 'high'], 'vibration'),
            ('Low Flow', ['medium', 'high'], 'flow'),
            ('Equipment Failure', ['critical'], 'failure'),
            ('Communication Loss', ['medium'], 'communication'),
            ('Low Level', ['low', 'medium'], 'level'),
            ('High Level', ['medium', 'high'], 'level')
        ]
        
        records = []
        for _ in range(total_alerts):
            alert_type, severities, category = random.choice(alert_types)
            severity = random.choice(severities)
            
            # Random timestamp within duration
            random_seconds = random.uniform(0, duration_days * 86400)
            alert_time = start_time + timedelta(seconds=random_seconds)
            
            # Random asset
            asset_id = f'asset_{random.randint(1, num_assets):03d}'
            
            # Threshold and actual values
            if category == 'temperature':
                threshold = 150.0
                actual = threshold + random.uniform(5, 30)
                unit = '°C'
            elif category == 'pressure':
                threshold = 1500.0
                actual = threshold + random.uniform(50, 200)
                unit = 'psi'
            elif category == 'vibration':
                threshold = 5.0
                actual = threshold + random.uniform(1, 5)
                unit = 'mm/s'
            elif category == 'flow':
                threshold = 100.0
                actual = threshold - random.uniform(20, 80)
                unit = 'm³/h'
            else:
                threshold = 0
                actual = 0
                unit = ''
            
            records.append({
                'timestamp': alert_time,
                'asset_id': asset_id,
                'alert_type': alert_type,
                'severity': severity,
                'category': category,
                'threshold_value': round(threshold, 2),
                'actual_value': round(actual, 2),
                'unit': unit,
                'description': f'{alert_type} detected on {asset_id}'
            })
        
        df = pd.DataFrame(records)
        return df.sort_values('timestamp').reset_index(drop=True)
    
    def generate_maintenance_events(
        self,
        start_date: datetime,
        duration_days: int,
        num_assets: int = 10
    ) -> pd.DataFrame:
        """
        Generate maintenance events
        
        Args:
            start_date: Start date
            duration_days: Duration in days
            num_assets: Number of assets
            
        Returns:
            DataFrame with maintenance events
        """
        maintenance_types = [
            ('Preventive Maintenance', 'scheduled', 4, 8),
            ('Inspection', 'scheduled', 2, 4),
            ('Corrective Maintenance', 'unscheduled', 8, 24),
            ('Calibration', 'scheduled', 1, 2),
            ('Repair', 'unscheduled', 4, 16)
        ]
        
        records = []
        event_id = 1
        
        for asset_id in range(1, num_assets + 1):
            current_date = start_date
            
            while current_date < start_date + timedelta(days=duration_days):
                # Random maintenance event every 15-30 days
                days_until_next = random.uniform(15, 30)
                current_date += timedelta(days=days_until_next)
                
                if current_date >= start_date + timedelta(days=duration_days):
                    break
                
                maint_type, schedule_type, min_hours, max_hours = random.choice(maintenance_types)
                duration_hours = random.uniform(min_hours, max_hours)
                cost = duration_hours * random.uniform(150, 300)  # $/hour
                
                records.append({
                    'event_id': f'maint_{event_id:04d}',
                    'asset_id': f'asset_{asset_id:03d}',
                    'maintenance_type': maint_type,
                    'schedule_type': schedule_type,
                    'start_date': current_date,
                    'duration_hours': round(duration_hours, 1),
                    'cost': round(cost, 2),
                    'technician': f'tech_{random.randint(1, 5):02d}',
                    'status': 'completed'
                })
                
                event_id += 1
        
        return pd.DataFrame(records)
    
    def generate_equipment_health_data(
        self,
        start_time: datetime,
        duration_days: int,
        num_equipment: int = 5,
        frequency_hours: int = 1
    ) -> pd.DataFrame:
        """
        Generate equipment health indicators
        
        Args:
            start_time: Start timestamp
            duration_days: Duration in days
            num_equipment: Number of equipment
            frequency_hours: Sampling frequency in hours
            
        Returns:
            DataFrame with health indicators
        """
        timestamps = pd.date_range(
            start=start_time,
            periods=duration_days * 24 // frequency_hours,
            freq=f'{frequency_hours}H'
        )
        
        records = []
        for equip_id in range(1, num_equipment + 1):
            # Equipment degradation over time
            initial_health = random.uniform(95, 100)
            degradation_rate = random.uniform(0.01, 0.05)  # % per day
            
            for idx, timestamp in enumerate(timestamps):
                days_elapsed = idx * frequency_hours / 24
                
                # Health score with degradation and noise
                health_score = initial_health - degradation_rate * days_elapsed
                health_score += np.random.normal(0, 2)
                health_score = max(0, min(100, health_score))
                
                # Related metrics
                vibration = 2 + (100 - health_score) * 0.1 + np.random.normal(0, 0.5)
                temperature = 70 + (100 - health_score) * 0.3 + np.random.normal(0, 2)
                efficiency = health_score - 10 + np.random.normal(0, 3)
                
                records.append({
                    'timestamp': timestamp,
                    'equipment_id': f'equip_{equip_id:03d}',
                    'health_score': round(health_score, 1),
                    'vibration_mm_s': round(max(0, vibration), 2),
                    'temperature_c': round(temperature, 1),
                    'efficiency_pct': round(max(0, min(100, efficiency)), 1),
                    'running_hours': round(days_elapsed * 24, 1),
                    'status': 'good' if health_score > 80 else 'warning' if health_score > 60 else 'critical'
                })
        
        return pd.DataFrame(records)


def generate_sample_dataset(output_dir: str = 'sample_data'):
    """Generate a sample dataset for testing"""
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    generator = SyntheticDataGenerator(seed=42)
    start_time = datetime(2024, 1, 1)
    
    print("Generating sample datasets...")
    
    # 1. Time-series sensor data (1 day at 1Hz - reduced for demo)
    print("  - Time-series sensor data (1 hour sample)...")
    ts_data = generator.generate_time_series(
        start_time=start_time,
        duration_days=1/24,  # 1 hour
        frequency_hz=1.0,
        num_sensors=10
    )
    ts_data.to_csv(f'{output_dir}/sensor_timeseries_1h.csv', index=False)
    print(f"    Generated {len(ts_data):,} sensor readings")
    
    # 2. Production data
    print("  - Production data (30 days)...")
    prod_data = generator.generate_production_data(
        start_date=start_time,
        duration_days=30,
        num_wells=5
    )
    prod_data.to_csv(f'{output_dir}/production_data_30d.csv', index=False)
    print(f"    Generated {len(prod_data):,} production records")
    
    # 3. Alert events
    print("  - Alert events (30 days)...")
    alert_data = generator.generate_alert_events(
        start_time=start_time,
        duration_days=30,
        num_assets=10,
        avg_alerts_per_day=2.0
    )
    alert_data.to_csv(f'{output_dir}/alert_events_30d.csv', index=False)
    print(f"    Generated {len(alert_data):,} alert events")
    
    # 4. Maintenance events
    print("  - Maintenance events (180 days)...")
    maint_data = generator.generate_maintenance_events(
        start_date=start_time,
        duration_days=180,
        num_assets=10
    )
    maint_data.to_csv(f'{output_dir}/maintenance_events_180d.csv', index=False)
    print(f"    Generated {len(maint_data):,} maintenance events")
    
    # 5. Equipment health data
    print("  - Equipment health data (30 days)...")
    health_data = generator.generate_equipment_health_data(
        start_time=start_time,
        duration_days=30,
        num_equipment=5,
        frequency_hours=1
    )
    health_data.to_csv(f'{output_dir}/equipment_health_30d.csv', index=False)
    print(f"    Generated {len(health_data):,} health records")
    
    print(f"\nAll sample data generated in '{output_dir}/' directory")
    print("\nFiles created:")
    for file in os.listdir(output_dir):
        filepath = os.path.join(output_dir, file)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  - {file}: {size_mb:.2f} MB")


if __name__ == "__main__":
    generate_sample_dataset()
