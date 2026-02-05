from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import List, Dict, Optional
from datetime import datetime
from .config import settings


class InfluxDBManager:
    """Manager for InfluxDB operations"""
    
    def __init__(self):
        self.client = None
        self.write_api = None
        self.query_api = None
        self._connect()
    
    def _connect(self):
        """Establish connection to InfluxDB"""
        if settings.INFLUXDB_TOKEN:
            self.client = InfluxDBClient(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
    
    def write_sensor_data(
        self,
        measurement: str,
        asset_id: str,
        sensor_id: str,
        value: float,
        timestamp: Optional[datetime] = None,
        additional_tags: Optional[Dict[str, str]] = None,
        additional_fields: Optional[Dict[str, any]] = None
    ):
        """
        Write sensor data to InfluxDB
        
        Args:
            measurement: Measurement name (e.g., 'temperature', 'pressure', 'flow_rate')
            asset_id: Asset identifier
            sensor_id: Sensor identifier
            value: Sensor reading value
            timestamp: Timestamp of the reading (defaults to now)
            additional_tags: Additional tags for indexing
            additional_fields: Additional field values
        """
        if not self.write_api:
            return
        
        point = Point(measurement)
        
        # Tags (indexed)
        point.tag("asset_id", asset_id)
        point.tag("sensor_id", sensor_id)
        
        if additional_tags:
            for key, val in additional_tags.items():
                point.tag(key, val)
        
        # Fields (values)
        point.field("value", value)
        
        if additional_fields:
            for key, val in additional_fields.items():
                point.field(key, val)
        
        # Timestamp
        if timestamp:
            point.time(timestamp, WritePrecision.NS)
        
        # Write to InfluxDB
        try:
            self.write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                org=settings.INFLUXDB_ORG,
                record=point
            )
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
    
    def write_batch_sensor_data(self, points: List[Point]):
        """
        Write multiple sensor readings in batch
        
        Args:
            points: List of Point objects to write
        """
        if not self.write_api:
            return
        
        try:
            self.write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                org=settings.INFLUXDB_ORG,
                record=points
            )
        except Exception as e:
            print(f"Error writing batch to InfluxDB: {e}")
    
    def query_sensor_data(
        self,
        measurement: str,
        asset_id: Optional[str] = None,
        sensor_id: Optional[str] = None,
        start_time: str = "-1h",
        stop_time: Optional[str] = None,
        aggregation_window: Optional[str] = None
    ) -> List[Dict]:
        """
        Query sensor data from InfluxDB
        
        Args:
            measurement: Measurement name
            asset_id: Filter by asset ID
            sensor_id: Filter by sensor ID
            start_time: Start time (e.g., '-1h', '-1d', '2024-01-01T00:00:00Z')
            stop_time: Stop time (defaults to now)
            aggregation_window: Aggregation window (e.g., '1m', '5m', '1h')
        
        Returns:
            List of data points
        """
        if not self.query_api:
            return []
        
        # Build Flux query
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: {start_time}'''
        
        if stop_time:
            query += f', stop: {stop_time}'
        
        query += f''')
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        '''
        
        if asset_id:
            query += f'    |> filter(fn: (r) => r["asset_id"] == "{asset_id}")\n'
        
        if sensor_id:
            query += f'    |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")\n'
        
        if aggregation_window:
            query += f'''
            |> aggregateWindow(every: {aggregation_window}, fn: mean, createEmpty: false)
            '''
        
        query += '    |> yield(name: "result")'
        
        try:
            tables = self.query_api.query(query, org=settings.INFLUXDB_ORG)
            
            results = []
            for table in tables:
                for record in table.records:
                    results.append({
                        'time': record.get_time(),
                        'asset_id': record.values.get('asset_id'),
                        'sensor_id': record.values.get('sensor_id'),
                        'value': record.get_value(),
                        'measurement': record.get_measurement()
                    })
            
            return results
        except Exception as e:
            print(f"Error querying InfluxDB: {e}")
            return []
    
    def get_latest_reading(
        self,
        measurement: str,
        asset_id: str,
        sensor_id: str
    ) -> Optional[Dict]:
        """
        Get the latest reading for a specific sensor
        
        Args:
            measurement: Measurement name
            asset_id: Asset identifier
            sensor_id: Sensor identifier
        
        Returns:
            Latest data point or None
        """
        if not self.query_api:
            return None
        
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: -24h)
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            |> filter(fn: (r) => r["asset_id"] == "{asset_id}")
            |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
            |> last()
        '''
        
        try:
            tables = self.query_api.query(query, org=settings.INFLUXDB_ORG)
            
            for table in tables:
                for record in table.records:
                    return {
                        'time': record.get_time(),
                        'asset_id': record.values.get('asset_id'),
                        'sensor_id': record.values.get('sensor_id'),
                        'value': record.get_value(),
                        'measurement': record.get_measurement()
                    }
            
            return None
        except Exception as e:
            print(f"Error querying latest reading from InfluxDB: {e}")
            return None
    
    def close(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()


# Global InfluxDB manager instance
influxdb_manager = InfluxDBManager()
